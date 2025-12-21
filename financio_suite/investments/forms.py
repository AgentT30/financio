from django import forms
from django.utils import timezone
from django.db import transaction
from .models import Investment, InvestmentTransaction, Broker

class BrokerForm(forms.ModelForm):
    class Meta:
        model = Broker
        fields = ['name', 'broker_user_id', 'demat_account_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'placeholder': 'e.g. Zerodha, Groww'
            }),
            'broker_user_id': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'placeholder': 'Client ID / User ID'
            }),
            'demat_account_number': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'placeholder': 'Demat Account Number'
            }),
        }

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['name', 'symbol', 'broker', 'investment_type', 'current_price', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'placeholder': 'e.g. Apple Inc., Nifty 50 ETF'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'placeholder': 'e.g. AAPL, INFY'
            }),
            'broker': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
            }),
            'investment_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
            }),
            'current_price': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'rows': 3
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter brokers by user and active status
        if user:
            self.fields['broker'].queryset = Broker.objects.filter(user=user, status='active')

class InvestmentTransactionForm(forms.ModelForm):
    class Meta:
        model = InvestmentTransaction
        fields = ['transaction_type', 'date', 'quantity', 'price_per_unit', 'fees', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'step': '1'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'step': '0.01'
            }),
            'fees': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'rows': 3
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
                'rows': 3
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        transaction_date = cleaned_data.get('date')
        price = cleaned_data.get('price_per_unit')
        fees = cleaned_data.get('fees')
        
        # Validate price is not negative
        if price is not None and price < 0:
            self.add_error('price_per_unit', 'Price per unit cannot be negative.')
        
        # Validate fees is not negative
        if fees is not None and fees < 0:
            self.add_error('fees', 'Fees cannot be negative.')
        
        # Validate quantity is greater than zero
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', 'Quantity must be greater than zero.')
        
        # Validate sell transactions when editing
        if transaction_type == 'sell' and quantity and self.instance and self.instance.pk:
            from decimal import Decimal
            investment = self.instance.investment
            
            # Calculate holdings up to this transaction date, excluding this transaction
            # This gives us the holdings available at the time of this transaction
            transactions = investment.transactions.exclude(pk=self.instance.pk).filter(
                date__lt=transaction_date
            ).order_by('date', 'created_at')
            
            # Also include transactions on the same date that were created before this one
            same_date_txns = investment.transactions.exclude(pk=self.instance.pk).filter(
                date=transaction_date,
                created_at__lt=self.instance.created_at
            ).order_by('created_at')
            
            # Combine both querysets
            from itertools import chain
            all_prior_txns = list(chain(transactions, same_date_txns))
            
            total_quantity = Decimal('0')
            for txn in all_prior_txns:
                if txn.transaction_type == 'buy':
                    total_quantity += txn.quantity
                elif txn.transaction_type == 'sell':
                    total_quantity -= txn.quantity
            
            # Check if the new sell quantity exceeds available holdings
            if quantity > total_quantity:
                self.add_error('quantity', f"Insufficient quantity. You own {total_quantity:.2f} units.")
        
        return cleaned_data

class InvestmentCreationForm(InvestmentForm):
    """
    Form for creating an investment AND its initial buy transaction in one step.
    """
    quantity = forms.DecimalField(
        max_digits=18, 
        decimal_places=0,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
            'step': '1',
            'placeholder': 'Number of units'
        }),
        help_text="Initial quantity purchased"
    )
    
    fees = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white',
            'step': '0.01',
            'placeholder': 'Transaction fees (optional)'
        }),
        help_text="Brokerage or other fees"
    )
    
    purchase_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
        }),
        help_text="Date of purchase"
    )

    transaction_type = forms.ChoiceField(
        choices=[('buy', 'Buy'), ('sell', 'Sell')],
        initial='buy',
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm dark:bg-dark-surface dark:border-gray-700 dark:text-white'
        }),
        help_text="Type of transaction"
    )

    class Meta(InvestmentForm.Meta):
        fields = ['name', 'symbol', 'broker', 'investment_type', 'transaction_type', 'current_price', 'quantity', 'fees', 'purchase_date', 'notes']

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.user = user  # Store user for save method
        # Make current_price required and label it appropriately
        self.fields['current_price'].required = True
        self.fields['current_price'].label = "Price"
        self.fields['current_price'].help_text = "Price per unit"
        self.fields['current_price'].initial = None
        self.fields['purchase_date'].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        name = cleaned_data.get('name')
        broker = cleaned_data.get('broker')
        quantity = cleaned_data.get('quantity')
        price = cleaned_data.get('current_price')
        fees = cleaned_data.get('fees')
        
        # Validate price is not negative
        if price is not None and price < 0:
            self.add_error('current_price', 'Price per unit cannot be negative.')
        
        # Validate fees is not negative
        if fees is not None and fees < 0:
            self.add_error('fees', 'Fees cannot be negative.')
        
        # Validate quantity is greater than zero
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', 'Quantity must be greater than zero.')

        if transaction_type == 'sell':
            # Check if investment exists
            existing_investment = Investment.objects.filter(
                user=self.user,
                name__iexact=name,
                broker=broker
            ).first()
            
            if not existing_investment:
                raise forms.ValidationError("Cannot sell an investment you do not own. Please check the name and broker.")
            
            # Check if enough quantity (simple check, model has more strict check but good to catch here)
            if quantity and existing_investment.total_quantity < quantity:
                 self.add_error('quantity', f"Insufficient quantity. You own {existing_investment.total_quantity:.2f} units.")

        return cleaned_data

    def save(self, commit=True):
        # Check if investment already exists
        name = self.cleaned_data.get('name')
        broker = self.cleaned_data.get('broker')
        txn_type = self.cleaned_data.get('transaction_type')
        
        existing_investment = Investment.objects.filter(
            user=self.user,
            name__iexact=name,
            broker=broker
        ).first()

        if existing_investment:
            investment = existing_investment
            # Update current price only if it's a buy (optional decision, or just update always as "latest market price")
            # Let's update it always to reflect latest activity price as a proxy for market price if user wants
            investment.current_price = self.cleaned_data['current_price']
            if commit:
                investment.save()
                
                with transaction.atomic():
                    InvestmentTransaction.objects.create(
                        investment=investment,
                        transaction_type=txn_type,
                        date=self.cleaned_data['purchase_date'],
                        quantity=self.cleaned_data['quantity'],
                        price_per_unit=self.cleaned_data['current_price'],
                        fees=self.cleaned_data.get('fees') or 0,
                        notes=self.cleaned_data.get('notes') or "Additional transaction"
                    )
            return investment
        
        # If not exists, create new (Only if Buy, but clean() handles Sell check)
        investment = super(InvestmentForm, self).save(commit=False)
        
        if self.user:
            investment.user = self.user
        
        if commit:
            with transaction.atomic():
                investment.save()
                
                # Create the initial transaction
                InvestmentTransaction.objects.create(
                    investment=investment,
                    transaction_type=txn_type,
                    date=self.cleaned_data['purchase_date'],
                    quantity=self.cleaned_data['quantity'],
                    price_per_unit=self.cleaned_data['current_price'], # Use current_price as buy price
                    fees=self.cleaned_data.get('fees') or 0,
                    notes=self.cleaned_data.get('notes') or "Initial purchase"
                )
        return investment
