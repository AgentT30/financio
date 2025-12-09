from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


from encrypted_model_fields.fields import EncryptedCharField

class Broker(models.Model):
    """
    Represents a stock broker or investment platform (e.g., Zerodha, Groww).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='brokers',
        help_text="Owner of the broker account"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the broker (e.g., Zerodha, Groww)"
    )
    broker_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="User ID/Client ID with the broker (alphanumeric)"
    )
    demat_account_number = EncryptedCharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Demat account number (encrypted)"
    )
    demat_account_number_last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        editable=False,
        help_text="Last 4 digits of demat account number"
    )
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Broker account status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brokers'
        verbose_name = 'Broker'
        verbose_name_plural = 'Brokers'
        unique_together = [['user', 'name']]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-extract last 4 digits
        if self.demat_account_number:
            clean_number = str(self.demat_account_number).replace(' ', '').replace('-', '')
            if len(clean_number) >= 4:
                self.demat_account_number_last4 = clean_number[-4:]
            else:
                self.demat_account_number_last4 = clean_number
        else:
            self.demat_account_number_last4 = None
        super().save(*args, **kwargs)

    def get_masked_account_number(self):
        if self.demat_account_number_last4:
            return f"****{self.demat_account_number_last4}"
        return "N/A"


class Investment(models.Model):
    """
    Represents an investment asset (e.g., Stock, Mutual Fund) held in a specific Broker account.
    """
    
    INVESTMENT_TYPE_CHOICES = [
        ('stock', 'Stock'),
        ('mutual_fund', 'Mutual Fund'),
        ('etf', 'ETF'),
        ('gold', 'Gold'),
        ('reit', 'REIT'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    # Ownership & Location
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='investments',
        help_text="Owner of the investment"
    )
    broker = models.ForeignKey(
        Broker,
        on_delete=models.PROTECT,
        related_name='investments',
        help_text="Broker where this investment is held"
    )

    # Asset Details
    name = models.CharField(
        max_length=100,
        help_text="Name of the asset (e.g., Apple Inc., Vanguard 500)"
    )
    symbol = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Ticker symbol (optional, e.g., AAPL)"
    )
    investment_type = models.CharField(
        max_length=20,
        choices=INVESTMENT_TYPE_CHOICES,
        default='stock',
        help_text="Type of investment asset"
    )
    
    # Valuation
    current_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Current market price per unit (manually updated)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Investment status"
    )
    
    # Additional Info
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investments'
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_inv_user_status'),
            models.Index(fields=['broker'], name='idx_inv_broker'),
        ]
        # Ensure unique asset per broker (optional, but good for data integrity)
        # We use name+symbol+broker as uniqueness constraint if symbol exists?
        # For now, let's just allow duplicates but maybe warn user.

    def __str__(self):
        if self.symbol:
            return f"{self.name} ({self.symbol}) - {self.broker.name}"
        return f"{self.name} - {self.broker.name}"

    def clean(self):
        # Validate that broker belongs to user
        if self.broker_id and self.user_id:
            if self.broker.user_id != self.user_id:
                raise ValidationError({'broker': "Broker must belong to the same user."})
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_holdings_data(self):
        """
        Calculate current holdings based on transactions.
        Returns a dictionary with quantity, average_price, invested_amount.
        """
        transactions = self.transactions.all().order_by('date', 'created_at')
        
        total_quantity = Decimal('0')
        total_cost = Decimal('0')
        
        for txn in transactions:
            if txn.transaction_type == 'buy':
                total_quantity += txn.quantity
                # Add cost: (price * qty) + fees
                total_cost += txn.total_amount
            elif txn.transaction_type == 'sell':
                if total_quantity > 0:
                    # Calculate proportional cost to remove
                    # Average cost per unit before this sell
                    avg_cost = total_cost / total_quantity
                    cost_removed = avg_cost * txn.quantity
                    
                    total_quantity -= txn.quantity
                    total_cost -= cost_removed
                    
                    # Ensure we don't go negative due to rounding
                    if total_quantity <= 0:
                        total_quantity = Decimal('0')
                        total_cost = Decimal('0')

        average_price = Decimal('0')
        if total_quantity > 0:
            average_price = total_cost / total_quantity

        return {
            'quantity': total_quantity,
            'average_price': average_price,
            'invested_amount': total_cost
        }

    @property
    def total_quantity(self):
        return self.get_holdings_data()['quantity']

    @property
    def average_buy_price(self):
        return self.get_holdings_data()['average_price']

    @property
    def total_invested(self):
        return self.get_holdings_data()['invested_amount']

    @property
    def current_value(self):
        return self.total_quantity * self.current_price

    @property
    def unrealized_pnl(self):
        return self.current_value - self.total_invested
        
    @property
    def unrealized_pnl_percentage(self):
        invested = self.total_invested
        if invested > 0:
            return (self.unrealized_pnl / invested) * 100
        return Decimal('0')


class InvestmentTransaction(models.Model):
    """
    Represents a Buy or Sell transaction for an investment.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    investment = models.ForeignKey(
        Investment,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="The investment asset being transacted"
    )
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of transaction"
    )
    
    date = models.DateField(
        default=timezone.now,
        help_text="Date of transaction"
    )
    
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Number of units bought/sold"
    )
    
    price_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Price per unit at time of transaction"
    )
    
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Brokerage, taxes, and other fees"
    )
    
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Total value of transaction (calculated)"
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investment_transactions'
        verbose_name = 'Investment Transaction'
        verbose_name_plural = 'Investment Transactions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.investment.name}"

    def clean(self):
        errors = {}
        
        # Validate quantity
        if self.quantity is not None and self.quantity <= 0:
            errors['quantity'] = "Quantity must be greater than zero."
            
        # Validate price
        if self.price_per_unit is not None and self.price_per_unit < 0:
            errors['price_per_unit'] = "Price per unit cannot be negative."
            
        # Validate fees
        if self.fees is not None and self.fees < 0:
            errors['fees'] = "Fees cannot be negative."

        # Validate Sell quantity (cannot sell more than owned)
        if self.transaction_type == 'sell' and self.quantity:
            # We need to check holdings BEFORE this transaction
            # Note: This is a simple check. For strict consistency, we might need more complex logic
            # handling edits/deletes of past transactions.
            # For now, we check current holdings if it's a new transaction.
            if not self.pk:  # Only for new transactions
                current_holdings = self.investment.total_quantity
                if self.quantity > current_holdings:
                    errors['quantity'] = f"Cannot sell {self.quantity} units. Current holdings: {current_holdings}."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        from decimal import Decimal, ROUND_HALF_UP
        
        # Round quantity to 2 decimal places (in case of legacy data with 4 decimals)
        if self.quantity:
            self.quantity = self.quantity.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate total amount
        if self.quantity and self.price_per_unit:
            base_amount = self.quantity * self.price_per_unit
            if self.transaction_type == 'buy':
                total = base_amount + (self.fees or 0)
            else:
                total = base_amount - (self.fees or 0)
            # Round to 2 decimal places
            self.total_amount = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        self.full_clean()
        super().save(*args, **kwargs)
