from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Transfer
from accounts.models import BankAccount


class TransferForm(forms.Form):
    """Form for creating transfers between accounts."""
    
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
        
        # Add account selection fields
        self.fields['from_account'] = forms.ModelChoiceField(
            queryset=BankAccount.objects.filter(user=self.user, status='active') if self.user else BankAccount.objects.none(),
            widget=forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            help_text="Select source account",
            empty_label="Choose source account"
        )
        
        self.fields['to_account'] = forms.ModelChoiceField(
            queryset=BankAccount.objects.filter(user=self.user, status='active') if self.user else BankAccount.objects.none(),
            widget=forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            help_text="Select destination account",
            empty_label="Choose destination account"
        )
    
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
        if from_account and to_account and from_account == to_account:
            raise ValidationError("Source and destination accounts must be different")
        
        # Validate amount is positive
        if amount and amount <= 0:
            raise ValidationError("Transfer amount must be greater than zero")
        
        return cleaned_data
