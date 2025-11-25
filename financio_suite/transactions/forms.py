from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Transaction
from categories.models import Category
from accounts.models import BankAccount
from core.utils import get_account_choices_for_form, get_account_from_compound_value


class CategorySelectWidget(forms.Select):
    """Custom Select widget that adds data-type attribute to options."""
    
    def __init__(self, category_types=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_types = category_types or {}
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # Extract just the category name from "Type: name" format and capitalize it
        if label and isinstance(label, str) and ':' in label:
            # Split "Income: salary" and take just "salary"
            label = label.split(':', 1)[1].strip().capitalize()
        elif label and isinstance(label, str):
            label = label.capitalize()
        
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        # Add data-type attribute to options (skip the empty option which has value='')
        if value:
            try:
                # Extract the actual value - it might be a ModelChoiceIteratorValue object
                actual_value = value.value if hasattr(value, 'value') else value
                int_value = int(actual_value)
                
                if int_value in self.category_types:
                    option['attrs']['data-type'] = self.category_types[int_value]
            except (ValueError, TypeError, AttributeError):
                pass
        
        return option


class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions."""
    
    # Custom fields for better UX
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
        }),
        help_text="Transaction date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Optional'
        }),
        required=False,
        initial=None,
        help_text="Transaction time (optional, defaults to current time if not provided)"
    )
    
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'method_type', 'purpose', 'category']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'method_type': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'purpose': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                'placeholder': 'Enter transaction description...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add custom account field with emoji indicators
        account_choices = [('', 'Choose an account')]  # Empty choice first
        if self.user:
            account_choices.extend(get_account_choices_for_form(self.user))
        
        self.fields['account'] = forms.ChoiceField(
            choices=account_choices,
            widget=forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            help_text="Select bank account or credit card",
            required=True
        )
        
        # Filter categories by user and add data-type attribute
        if self.user:
            categories = Category.objects.filter(
                user=self.user,
                is_active=True,
                type__in=['income', 'expense']  # Only show income and expense categories
            ).order_by('type', 'name')
            
            # Build category types mapping for custom widget
            category_types = {cat.id: cat.type for cat in categories}
            
            # Replace widget with custom widget that includes data-type
            self.fields['category'].widget = CategorySelectWidget(
                category_types=category_types,
                attrs={
                    'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
                }
            )
            
            # Now set the queryset and empty_label AFTER setting the widget
            self.fields['category'].queryset = categories
            self.fields['category'].empty_label = "Choose a category (optional)"
        
        # Set initial date/time if editing
        if self.instance and self.instance.pk:
            self.fields['date'].initial = self.instance.datetime_ist.date()
            self.fields['time'].initial = self.instance.datetime_ist.time()
            # Set account field for editing - need to reconstruct compound value
            if self.instance.account_object_id and self.instance.account_content_type:
                model_name = self.instance.account_content_type.model
                compound_value = f"{self.instance.account_object_id}|{model_name}"
                self.fields['account'].initial = compound_value
    
    def clean_account(self):
        """Extract actual account object from compound value."""
        account_value = self.cleaned_data.get('account')
        
        if not account_value:
            raise ValidationError("Please select an account")
        
        try:
            # Use helper function to get actual account object
            account = get_account_from_compound_value(account_value, self.user)
            return account
        except ValueError as e:
            raise ValidationError(str(e))
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        account = cleaned_data.get('account')
        transaction_type = cleaned_data.get('transaction_type')
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
        
        # Set GenericFK fields from account
        if account:
            from django.contrib.contenttypes.models import ContentType
            cleaned_data['account_content_type'] = ContentType.objects.get_for_model(account)
            cleaned_data['account_object_id'] = account.pk
        
        # Validate sufficient balance for expense transactions on bank accounts
        if account and transaction_type == 'expense' and amount:
            account_type = account.__class__.__name__
            
            # Only check balance for BankAccount (credit cards can go more negative)
            if account_type == 'BankAccount':
                current_balance = account.get_current_balance()
                
                if current_balance < amount:
                    raise ValidationError(
                        f"Insufficient balance in {account.name}. "
                        f"Current balance: ₹{current_balance:,.2f}, "
                        f"Expense amount: ₹{amount:,.2f}. "
                        f"Please reduce the amount or use a different account."
                    )
        
        return cleaned_data
