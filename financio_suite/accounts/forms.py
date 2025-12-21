from django import forms
from django.core.exceptions import ValidationError
from .models import BankAccount


class BankAccountForm(forms.ModelForm):
    """Form for creating and editing bank accounts."""

    class Meta:
        model = BankAccount
        fields = [
            'name', 'account_type', 'institution', 'branch_name', 'ifsc_code',
            'customer_id', 'account_number', 'opening_balance', 'opened_on',
            'status', 'notes', 'picture', 'color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Account name (e.g., HDFC Salary Account)'
            }),
            'account_type': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Bank/Institution name (e.g., HDFC Bank)'
            }),
            'branch_name': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Branch name (optional)'
            }),
            'ifsc_code': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent uppercase',
                'placeholder': 'IFSC Code (e.g., SBIN0001234)',
                'maxlength': '11'
            }),
            'customer_id': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Customer ID (optional)'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Account number (encrypted)'
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
            'status': forms.Select(attrs={
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make optional fields clear
        self.fields['institution'].required = False
        self.fields['branch_name'].required = False
        self.fields['ifsc_code'].required = False
        self.fields['customer_id'].required = False
        self.fields['account_number'].required = False
        self.fields['opened_on'].required = False
        self.fields['notes'].required = False
        self.fields['picture'].required = False
        self.fields['color'].required = False

    def clean_ifsc_code(self):
        """Validate and uppercase IFSC code"""
        ifsc = self.cleaned_data.get('ifsc_code')
        if ifsc:
            return ifsc.upper()
        return ifsc
