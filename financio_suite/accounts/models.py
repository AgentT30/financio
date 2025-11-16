import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField


class Account(models.Model):
    """
    Account model for managing user's financial accounts.
    Supports multiple account types with encrypted sensitive data.
    """
    
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings Account'),
        ('credit_card', 'Credit Card'),
        ('wallet', 'Digital Wallet'),
        ('cash', 'Cash'),
        ('fd', 'Fixed Deposit'),
        ('loan', 'Loan Account'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accounts',
        db_index=True,
        help_text="Account owner"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name/nickname for the account"
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of account"
    )
    
    # Institution Details
    institution = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Bank or financial institution name"
    )
    branch_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Branch name"
    )
    ifsc_code = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        help_text="IFSC code (11 characters)"
    )
    customer_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Customer ID with the institution"
    )
    
    # Account Identifiers (Encrypted)
    account_number = EncryptedCharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Full account number (encrypted)"
    )
    account_number_last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        editable=False,
        help_text="Last 4 digits of account number (for display)"
    )
    
    # Financial Information
    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        help_text="Initial balance when account was opened"
    )
    currency = models.CharField(
        max_length=3,
        default='INR',
        help_text="Currency code (fixed to INR for V1)"
    )
    
    # Dates and Status
    opened_on = models.DateField(
        null=True,
        blank=True,
        help_text="Date when account was opened"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Account status"
    )
    
    # Optional Links to FD/Loan (to be implemented later)
    # fd_details = models.OneToOneField('fds.FD', null=True, blank=True, on_delete=models.SET_NULL)
    # loan_details = models.OneToOneField('loans.Loan', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about the account"
    )
    
    # Visual Customization
    picture = models.ImageField(
        upload_to='account_pictures/',
        null=True,
        blank=True,
        help_text="Account picture/icon (optional)"
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Color theme for account (hex code, e.g., #3B82F6)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when account was last updated"
    )
    
    class Meta:
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
        unique_together = [['user', 'institution', 'account_number_last4']]
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_acc_user_status'),
            models.Index(fields=['account_type'], name='idx_acc_type'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    def clean(self):
        """Validate account data"""
        # Validate IFSC code format if provided
        if self.ifsc_code:
            if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', self.ifsc_code):
                raise ValidationError({
                    'ifsc_code': 'Invalid IFSC code format. Must be 11 characters (e.g., SBIN0001234)'
                })
        
        # Validate currency is INR for V1
        if self.currency != 'INR':
            raise ValidationError({
                'currency': 'Only INR currency is supported in V1'
            })
        
        # Validate color format if provided
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError({
                'color': 'Color must be a valid hex code (e.g., #3B82F6)'
            })
    
    def save(self, *args, **kwargs):
        """Override save to auto-extract last 4 digits and run validation"""
        # Auto-extract last 4 digits from account number
        if self.account_number:
            # Remove any spaces or dashes
            clean_number = str(self.account_number).replace(' ', '').replace('-', '')
            if len(clean_number) >= 4:
                self.account_number_last4 = clean_number[-4:]
            else:
                self.account_number_last4 = clean_number
        else:
            self.account_number_last4 = None
        
        # Run validations
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_masked_account_number(self):
        """Returns masked account number (e.g., '****1234')"""
        if self.account_number_last4:
            return f"****{self.account_number_last4}"
        return "N/A"
    
    def get_current_balance(self):
        """
        Get current balance from AccountBalance model.
        Returns opening_balance if no balance record exists yet.
        """
        try:
            return self.balance.balance_amount
        except AccountBalance.DoesNotExist:
            return self.opening_balance
    
    def can_delete(self):
        """Check if account can be deleted (no transactions)"""
        # Will implement when Transaction model exists
        # For now, return True
        return True
    
    def archive(self):
        """Archive the account (soft delete)"""
        self.status = 'archived'
        self.save(update_fields=['status', 'updated_at'])
    
    def activate(self):
        """Activate an archived account"""
        self.status = 'active'
        self.save(update_fields=['status', 'updated_at'])


class AccountBalance(models.Model):
    """
    Materialized balance table for fast balance lookups.
    Updated atomically when transactions/postings are created.
    """
    
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='balance',
        help_text="Associated account"
    )
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        help_text="Current balance (materialized from ledger)"
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
        db_table = 'account_balances'
        verbose_name = 'Account Balance'
        verbose_name_plural = 'Account Balances'
    
    def __str__(self):
        return f"{self.account.name}: {self.balance_amount} {self.account.currency}"

