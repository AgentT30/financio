from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Transfer
from accounts.models import BankAccount
from core.utils import get_account_choices_for_form, get_account_from_compound_value


class TransferForm(forms.Form):
    """
    Form for creating transfers between accounts.

    Supports transfers between any account types including:
    - Bank → Bank (standard inter-account transfer)
    - Bank → Credit Card (bill payment - reduces credit card debt)
    - Credit Card → Bank (refund/reversal - increases credit card debt)
    - Credit Card → Credit Card (balance transfer between cards)

    Features:
    - Unified account dropdown with emoji indicators (🏦 Bank, 💳 Credit Card)
    - Three-layer validation (form, model, service) prevents same-account transfers
    - Insufficient balance validation for bank accounts (credit cards exempt)
    - Compound value format for account selection: "id|modelname"

    Validation:
    - Prevents transfer to same account (compares ContentType ID + object ID)
    - Validates bank account has sufficient balance
    - Amount must be > 0
    - Both accounts must belong to same user
    """

    # Date and time fields
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
        }),
        help_text="Transfer date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Optional'
        }),
        required=False,
        initial=None,
        help_text="Transfer time (optional, defaults to current time if not provided)"
    )

    # Amount
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )

    # Method type
    method_type = forms.ChoiceField(
        choices=Transfer.METHOD_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )

    # Memo
    memo = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
            'placeholder': 'Enter transfer description...'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Get account choices with emoji indicators
        account_choices = [('', 'Choose an account')]  # Empty choice first
        if self.user:
            account_choices.extend(get_account_choices_for_form(self.user))

        # Add from_account field with unified dropdown
        self.fields['from_account'] = forms.ChoiceField(
            choices=account_choices,
            widget=forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            help_text="Select source account (bank or credit card)",
            required=True
        )

        # Add to_account field with unified dropdown
        self.fields['to_account'] = forms.ChoiceField(
            choices=account_choices,
            widget=forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            help_text="Select destination account (bank or credit card)",
            required=True
        )

    def clean_from_account(self):
        """Extract actual account object from compound value for from_account."""
        account_value = self.cleaned_data.get('from_account')

        if not account_value:
            raise ValidationError("Please select a source account")

        try:
            account = get_account_from_compound_value(account_value, self.user)
            return account
        except ValueError as e:
            raise ValidationError(str(e))

    def clean_to_account(self):
        """Extract actual account object from compound value for to_account."""
        account_value = self.cleaned_data.get('to_account')

        if not account_value:
            raise ValidationError("Please select a destination account")

        try:
            account = get_account_from_compound_value(account_value, self.user)
            return account
        except ValueError as e:
            raise ValidationError(str(e))

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        amount = cleaned_data.get('amount')

        # Combine date and time
        if date:
            if time:
                datetime_ist = timezone.datetime.combine(date, time)
            else:
                datetime_ist = timezone.datetime.combine(date, timezone.now().time())

            # Make timezone-aware (IST)
            datetime_ist = timezone.make_aware(datetime_ist, timezone.get_current_timezone())
            cleaned_data['datetime_ist'] = datetime_ist

        # Validate from_account and to_account are different
        # This validation is also in the model, but we check here for better UX
        if from_account and to_account:
            from django.contrib.contenttypes.models import ContentType
            from_ct = ContentType.objects.get_for_model(from_account)
            to_ct = ContentType.objects.get_for_model(to_account)

            # Same account only if BOTH content type AND object ID match
            # Example: Bank(id=1) != CreditCard(id=1) even if IDs match
            # Example: Bank(id=1) == Bank(id=1) only if type + ID both match
            if from_ct.id == to_ct.id and from_account.id == to_account.id:
                raise ValidationError("Source and destination accounts must be different")

        # Validate amount is positive
        if amount and amount <= 0:
            raise ValidationError("Transfer amount must be greater than zero")

        # Validate sufficient balance for bank accounts
        if from_account and amount:
            from_account_type = from_account.__class__.__name__

            # Only check balance for BankAccount (credit cards can go more negative)
            # Transfers from credit cards are valid (e.g., refund/reversal scenarios)
            if from_account_type == 'BankAccount':
                current_balance = from_account.get_current_balance()

                if current_balance < amount:
                    raise ValidationError(
                        f"Insufficient balance in {from_account.name}. "
                        f"Current balance: ₹{current_balance:,.2f}, "
                        f"Transfer amount: ₹{amount:,.2f}. "
                        f"Please reduce the transfer amount or add funds to the account."
                    )

        return cleaned_data
