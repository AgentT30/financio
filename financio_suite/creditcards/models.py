import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField
from core.models import BaseAccount
from datetime import date


class CreditCard(BaseAccount):
    """
    Credit card account model for managing user's credit cards.
    Supports multiple card types with encrypted sensitive data.
    Inherits common fields from BaseAccount.
    """
    
    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('rupay', 'RuPay'),
        ('amex', 'American Express'),
    ]
    
    # Institution Details
    institution = models.CharField(
        max_length=100,
        help_text="Issuing bank or financial institution"
    )
    
    # Card Identifiers (Encrypted)
    card_number = EncryptedCharField(
        max_length=100,
        help_text="Full card number (encrypted)"
    )
    card_number_last4 = models.CharField(
        max_length=4,
        editable=False,
        help_text="Last 4 digits of card number (for display)"
    )
    cvv = EncryptedCharField(
        max_length=10,
        help_text="Card CVV/CVV2 (encrypted)"
    )
    
    # Card Type
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        default='visa',
        db_index=True,
        help_text="Type of credit card"
    )
    
    # Credit Limit and Billing
    credit_limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Total credit limit on the card"
    )
    billing_day = models.IntegerField(
        help_text="Day of month when billing cycle starts (1-31)"
    )
    due_day = models.IntegerField(
        help_text="Day of month when payment is due (1-31)"
    )
    expiry_date = models.DateField(
        help_text="Card expiry date (MM/YY)"
    )
    
    class Meta:
        db_table = 'credit_cards'
        verbose_name = 'Credit Card'
        verbose_name_plural = 'Credit Cards'
        unique_together = [['user', 'institution', 'card_number_last4']]
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_cc_user_status'),
            models.Index(fields=['card_type'], name='idx_cc_type'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_card_type_display()} ****{self.card_number_last4})"
    
    def clean(self):
        """Validate credit card data"""
        # Call parent validation
        super().clean()
        
        # Validate card number (basic check - should be digits only)
        if self.card_number:
            clean_number = str(self.card_number).replace(' ', '').replace('-', '')
            if not clean_number.isdigit():
                raise ValidationError({
                    'card_number': 'Card number must contain only digits'
                })
            
            # Validate card number length (13-19 digits typical)
            if len(clean_number) < 13 or len(clean_number) > 19:
                raise ValidationError({
                    'card_number': 'Card number must be between 13 and 19 digits'
                })
        
        # Validate CVV (3-4 digits)
        if self.cvv:
            clean_cvv = str(self.cvv).strip()
            if not clean_cvv.isdigit():
                raise ValidationError({
                    'cvv': 'CVV must contain only digits'
                })
            if len(clean_cvv) < 3 or len(clean_cvv) > 4:
                raise ValidationError({
                    'cvv': 'CVV must be 3 or 4 digits'
                })
        
        # Validate billing day (1-31)
        if self.billing_day:
            if self.billing_day < 1 or self.billing_day > 31:
                raise ValidationError({
                    'billing_day': 'Billing day must be between 1 and 31'
                })
        
        # Validate due day (1-31)
        if self.due_day:
            if self.due_day < 1 or self.due_day > 31:
                raise ValidationError({
                    'due_day': 'Due day must be between 1 and 31'
                })
        
        # Validate expiry date (should be in future)
        if self.expiry_date:
            if self.expiry_date < date.today():
                raise ValidationError({
                    'expiry_date': 'Card has expired. Expiry date must be in the future.'
                })
        
        # Validate credit limit (must be positive)
        if self.credit_limit is not None and self.credit_limit <= 0:
            raise ValidationError({
                'credit_limit': 'Credit limit must be a positive amount'
            })
    
    def save(self, *args, **kwargs):
        """Override save to auto-extract last 4 digits and run validation"""
        # Auto-extract last 4 digits from card number
        if self.card_number:
            # Remove any spaces or dashes
            clean_number = str(self.card_number).replace(' ', '').replace('-', '')
            if len(clean_number) >= 4:
                self.card_number_last4 = clean_number[-4:]
            else:
                self.card_number_last4 = clean_number
        
        # Run validations
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_masked_card_number(self):
        """Returns masked card number (e.g., '****1234')"""
        if self.card_number_last4:
            return f"****{self.card_number_last4}"
        return "N/A"
    
    def get_masked_cvv(self):
        """Returns masked CVV (e.g., '***')"""
        if self.cvv:
            return '***'
        return "N/A"
    
    def get_current_balance(self):
        """
        Get current balance from CreditCardBalance model.
        Returns opening_balance if no balance record exists yet.
        
        Note: For credit cards, negative balance = amount owed (liability)
              Positive balance = overpayment (rare, but possible)
        """
        try:
            return self.balance.balance_amount
        except CreditCardBalance.DoesNotExist:
            return self.opening_balance
    
    def available_credit(self):
        """
        Calculate available credit.
        Available = Credit Limit - Current Balance (absolute value)
        
        For credit cards:
        - Balance of -5000 means you owe ₹5000
        - If credit limit is ₹50,000, available credit = ₹45,000
        """
        current_balance = self.get_current_balance()
        # If balance is negative (debt), available = limit + balance (since balance is negative)
        # If balance is positive (overpayment), available = limit + balance
        return self.credit_limit + current_balance
    
    def amount_owed(self):
        """
        Calculate amount owed (absolute value of negative balance).
        Returns 0 if balance is positive (overpayment).
        """
        current_balance = self.get_current_balance()
        return abs(min(current_balance, 0))
    
    def can_delete(self):
        """Check if credit card can be deleted (no transactions or transfers)"""
        from django.contrib.contenttypes.models import ContentType
        from transactions.models import Transaction
        from transfers.models import Transfer
        from django.db.models import Q
        
        # Get ContentType for this credit card
        account_content_type = ContentType.objects.get_for_model(CreditCard)
        
        # Check if card has any non-deleted transactions
        has_transactions = Transaction.objects.filter(
            account_content_type=account_content_type,
            account_object_id=self.id,
            deleted_at__isnull=True
        ).exists()
        
        if has_transactions:
            return False
        
        # Check if card has any non-deleted transfers (either as from or to account)
        has_transfers = Transfer.objects.filter(
            Q(from_account_content_type=account_content_type, from_account_object_id=self.id) |
            Q(to_account_content_type=account_content_type, to_account_object_id=self.id),
            deleted_at__isnull=True
        ).exists()
        
        if has_transfers:
            return False
        
        return True


class CreditCardBalance(models.Model):
    """
    Materialized balance table for fast balance lookups.
    Updated atomically when transactions/postings are created.
    
    For credit cards:
    - Negative balance = amount owed (liability)
    - Positive balance = overpayment (rare scenario)
    """
    
    account = models.OneToOneField(
        CreditCard,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='balance',
        help_text="Associated credit card"
    )
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        help_text="Current balance (negative = owed, positive = overpayment)"
    )
    last_posting_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="ID of last posting that updated this balance"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last balance update"
    )
    
    class Meta:
        db_table = 'credit_card_balances'
        verbose_name = 'Credit Card Balance'
        verbose_name_plural = 'Credit Card Balances'
    
    def __str__(self):
        return f"{self.account.name}: {self.balance_amount} {self.account.currency}"
