from django import forms
from django.core.exceptions import ValidationError
from .models import FixedDeposit


class FixedDepositForm(forms.ModelForm):
    """Form for creating and editing fixed deposits."""

    class Meta:
        model = FixedDeposit
        fields = [
            'name', 'institution', 'fd_number',
            'principal_amount', 'interest_rate', 'maturity_amount',
            'compounding_frequency', 'tenure_months', 'auto_renewal',
            'opened_on', 'maturity_date',
            'status', 'notes', 'color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'FD name (e.g., HDFC 5-Year FD)'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Bank name (e.g., HDFC Bank)'
            }),
            'fd_number': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'FD certificate number (optional)'
            }),
            'principal_amount': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '100000.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '6.50',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'maturity_amount': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '135000.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'compounding_frequency': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'tenure_months': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '60',
                'min': '1'
            }),
            'auto_renewal': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded border-gray-300 dark:border-gray-600 text-primary focus:ring-2 focus:ring-primary focus:ring-offset-0 dark:bg-dark-surface dark:checked:bg-primary'
            }),
            'opened_on': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'maturity_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                'placeholder': 'Additional notes about this FD (optional)'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-14 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
        }
        help_texts = {
            'name': 'A memorable name for this FD',
            'institution': 'Name of the bank where FD is held',
            'fd_number': 'FD certificate or account number (if available)',
            'principal_amount': 'Amount deposited (must be greater than 0)',
            'interest_rate': 'Annual interest rate in percentage (0-100%)',
            'maturity_amount': 'Total amount you will receive on maturity (including interest)',
            'compounding_frequency': 'How often interest is compounded',
            'tenure_months': 'FD duration in months',
            'auto_renewal': 'Check if FD will auto-renew on maturity',
            'opened_on': 'Date when FD was opened',
            'maturity_date': 'Date when FD will mature (must be after opening date)',
            'status': 'Current status of the FD',
            'notes': 'Any additional information or notes',
            'color': 'Color code for visual identification',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make optional fields clear
        self.fields['fd_number'].required = False
        self.fields['notes'].required = False
        self.fields['color'].required = False

        # For archived FDs, disable editing (should not happen in normal flow)
        if self.instance and self.instance.pk and self.instance.status == 'archived':
            for field in self.fields:
                self.fields[field].disabled = True

    def clean(self):
        """Additional validation and auto-attach user"""
        cleaned_data = super().clean()

        principal = cleaned_data.get('principal_amount')
        maturity = cleaned_data.get('maturity_amount')
        opened_on = cleaned_data.get('opened_on')
        maturity_date = cleaned_data.get('maturity_date')
        interest_rate = cleaned_data.get('interest_rate')
        tenure_months = cleaned_data.get('tenure_months')

        # Validate principal amount
        if principal is not None and principal <= 0:
            raise ValidationError({
                'principal_amount': 'Principal amount must be greater than zero.'
            })

        # Validate interest rate range
        if interest_rate is not None:
            if interest_rate < 0 or interest_rate > 100:
                raise ValidationError({
                    'interest_rate': 'Interest rate must be between 0 and 100%.'
                })

        # Validate maturity amount vs principal
        if principal is not None and maturity is not None:
            if maturity < principal:
                raise ValidationError({
                    'maturity_amount': f'Maturity amount (₹{maturity:,.2f}) cannot be less than principal amount (₹{principal:,.2f}).'
                })

        # Validate tenure months
        if tenure_months is not None and tenure_months <= 0:
            raise ValidationError({
                'tenure_months': 'Tenure must be greater than zero months.'
            })

        # Validate dates
        if opened_on and maturity_date:
            if maturity_date <= opened_on:
                raise ValidationError({
                    'maturity_date': f'Maturity date must be after opening date ({opened_on.strftime("%d/%m/%Y")}).'
                })

        return cleaned_data

    def clean_principal_amount(self):
        """Validate principal amount"""
        principal = self.cleaned_data.get('principal_amount')
        if principal is not None and principal <= 0:
            raise ValidationError('Principal amount must be greater than zero.')
        return principal

    def clean_interest_rate(self):
        """Validate interest rate"""
        rate = self.cleaned_data.get('interest_rate')
        if rate is not None:
            if rate < 0:
                raise ValidationError('Interest rate cannot be negative.')
            if rate > 100:
                raise ValidationError('Interest rate cannot exceed 100%.')
        return rate

    def clean_maturity_amount(self):
        """Validate maturity amount"""
        maturity = self.cleaned_data.get('maturity_amount')
        if maturity is not None and maturity <= 0:
            raise ValidationError('Maturity amount must be greater than zero.')
        return maturity

    def clean_tenure_months(self):
        """Validate tenure months"""
        tenure = self.cleaned_data.get('tenure_months')
        if tenure is not None and tenure <= 0:
            raise ValidationError('Tenure must be at least 1 month.')
        return tenure
