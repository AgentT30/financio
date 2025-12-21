from django import forms
from .models import CreditCard
from datetime import date


class CreditCardForm(forms.ModelForm):
    """
    Form for creating and editing credit cards.
    Includes validation for card-specific fields.
    """

    class Meta:
        model = CreditCard
        fields = [
            'name',
            'institution',
            'card_number',
            'cvv',
            'card_type',
            'credit_limit',
            'billing_day',
            'due_day',
            'expiry_date',
            'opening_balance',
            'opened_on',
            'notes',
            'picture',
            'color',
            'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Card name (e.g., HDFC Regalia)'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Issuing bank (e.g., HDFC Bank)'
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Card number (encrypted)',
                'autocomplete': 'off'
            }),
            'cvv': forms.PasswordInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'CVV',
                'maxlength': '4',
                'autocomplete': 'off'
            }),
            'card_type': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'billing_day': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '1',
                'min': '1',
                'max': '31'
            }),
            'due_day': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '20',
                'min': '1',
                'max': '31'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'opened_on': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                'placeholder': 'Additional notes (optional)'
            }),
            'picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-14 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
        }
        help_texts = {
            'name': 'Display name or nickname for the card',
            'institution': 'Issuing bank or financial institution',
            'card_number': 'Full card number (will be encrypted)',
            'cvv': 'Card CVV/CVV2 (will be encrypted)',
            'card_type': 'Select the card network',
            'credit_limit': 'Total credit limit on this card',
            'billing_day': 'Day of month when billing cycle starts (1-31)',
            'due_day': 'Day of month when payment is due (1-31)',
            'expiry_date': 'Card expiry date',
            'opening_balance': 'Initial balance (usually 0, negative if you owe)',
            'opened_on': 'Date when card was issued',
            'notes': 'Optional notes',
            'picture': 'Upload card picture/logo (optional)',
            'color': 'Color theme for the card',
            'status': 'Card status (active or archived)',
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with user instance"""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set initial values for new cards
        if not self.instance.pk:
            self.fields['status'].initial = 'active'
            self.fields['opening_balance'].initial = 0.00
            if self.user:
                # Auto-set opened_on to today for new cards
                self.fields['opened_on'].initial = date.today()
        else:
            # For existing cards, preserve CVV by not requiring it to be re-entered
            self.fields['cvv'].required = False
            # If CVV exists, show placeholder instead of clearing
            if self.instance.cvv:
                self.fields['cvv'].widget.attrs['placeholder'] = '•••'

    def clean_card_number(self):
        """Validate card number format"""
        card_number = self.cleaned_data.get('card_number')
        if card_number:
            # Remove spaces and dashes
            clean_number = str(card_number).replace(' ', '').replace('-', '')

            # Check if digits only
            if not clean_number.isdigit():
                raise forms.ValidationError('Card number must contain only digits')

            # Check length
            if len(clean_number) < 13 or len(clean_number) > 19:
                raise forms.ValidationError('Card number must be between 13 and 19 digits')

            return clean_number
        return card_number

    def clean_cvv(self):
        """Validate CVV format"""
        cvv = self.cleaned_data.get('cvv')

        # If editing and CVV is empty, keep the existing value
        if self.instance.pk and not cvv:
            return self.instance.cvv

        if cvv:
            clean_cvv = str(cvv).strip()

            # Check if digits only
            if not clean_cvv.isdigit():
                raise forms.ValidationError('CVV must contain only digits')

            # Check length
            if len(clean_cvv) < 3 or len(clean_cvv) > 4:
                raise forms.ValidationError('CVV must be 3 or 4 digits')

            return clean_cvv
        return cvv

    def clean_expiry_date(self):
        """Validate expiry date is in future"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            if expiry_date < date.today():
                raise forms.ValidationError('Card has expired. Expiry date must be in the future.')
        return expiry_date

    def clean_credit_limit(self):
        """Validate credit limit is positive"""
        credit_limit = self.cleaned_data.get('credit_limit')
        if credit_limit is not None and credit_limit <= 0:
            raise forms.ValidationError('Credit limit must be a positive amount')
        return credit_limit

    def clean(self):
        """Additional form-level validation"""
        cleaned_data = super().clean()
        billing_day = cleaned_data.get('billing_day')
        due_day = cleaned_data.get('due_day')

        # Validate billing and due days are different
        if billing_day and due_day and billing_day == due_day:
            raise forms.ValidationError(
                'Billing day and due day should be different'
            )

        return cleaned_data

    def save(self, commit=True):
        """Save the credit card with user assignment"""
        creditcard = super().save(commit=False)
        if self.user and not creditcard.user_id:
            creditcard.user = self.user
        if commit:
            creditcard.save()
        return creditcard
