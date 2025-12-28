import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField
from core.models import BaseAccount


class BankAccount(BaseAccount):
    """
    Bank account model for managing user's financial accounts.
    Supports multiple account types with encrypted sensitive data.
    Inherits common fields from BaseAccount.
    """

    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings Account'),
        ('checking', 'Checking Account'),
        ('current', 'Current Account'),
        ('salary', 'Salary Account'),
    ]

    # Account Type (specific to bank accounts)
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='savings',
        db_index=True,
        help_text="Type of bank account"
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

    class Meta:
        db_table = 'bank_accounts'
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        unique_together = [['user', 'institution', 'account_number_last4']]
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_bank_acc_user_status'),
            models.Index(fields=['account_type'], name='idx_bank_acc_type'),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    def clean(self):
        """Validate account data"""
        # Call parent validation
        super().clean()

        # Validate IFSC code format if provided
        if self.ifsc_code:
            if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', self.ifsc_code):
                raise ValidationError({
                    'ifsc_code': 'Invalid IFSC code format. Must be 11 characters (e.g., SBIN0001234)'
                })

    def save(self, *args, **kwargs):
        """Override save to auto-extract last 4 digits and run validation and normalize storage"""
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
        """
        Returns masked account number showing only last 4 digits.

        Returns:
            str: Masked format '****1234' or 'N/A' if account number not set

        Example:
            Account number: 123456789012 → '****9012'
        """
        if self.account_number_last4:
            return f"****{self.account_number_last4}"
        return "N/A"

    def get_current_balance(self):
        """
        Get current balance from BankAccountBalance materialized table.

        Provides graceful degradation - if balance record doesn't exist
        (e.g., was deleted during testing), returns opening_balance as fallback.

        This method is used by dashboard and account list views to ensure
        robust balance calculations even when balance records are missing.

        Returns:
            Decimal: Current account balance from materialized table,
                    or opening_balance if balance record missing
        """
        try:
            return self.balance.balance_amount
        except BankAccountBalance.DoesNotExist:
            return self.opening_balance

    def can_delete(self):
        """
        Check if account can be safely deleted.

        An account can only be deleted if it has no associated transactions
        or transfers. This prevents orphaning financial records.

        Returns:
            bool: True if account can be deleted, False if it has dependencies

        Note:
            Only checks non-deleted (active) transactions and transfers.
            Uses GenericForeignKey to check both transaction and transfer tables.
        """
        from django.contrib.contenttypes.models import ContentType
        from transactions.models import Transaction
        from transfers.models import Transfer
        from django.db.models import Q

        # Get ContentType for this account
        account_content_type = ContentType.objects.get_for_model(BankAccount)

        # Check if account has any non-deleted transactions
        has_transactions = Transaction.objects.filter(
            account_content_type=account_content_type,
            account_object_id=self.id,
            deleted_at__isnull=True
        ).exists()

        if has_transactions:
            return False

        # Check if account has any non-deleted transfers (either as from or to account)
        has_transfers = Transfer.objects.filter(
            Q(from_account_content_type=account_content_type, from_account_object_id=self.id) |
            Q(to_account_content_type=account_content_type, to_account_object_id=self.id),
            deleted_at__isnull=True
        ).exists()

        if has_transfers:
            return False

        return True


class BankAccountBalance(models.Model):
    """
    Materialized balance table for fast balance lookups.
    Updated atomically when transactions/postings are created.
    """

    account = models.OneToOneField(
        BankAccount,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='balance',
        help_text="Associated bank account"
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
        db_table = 'bank_account_balances'
        verbose_name = 'Bank Account Balance'
        verbose_name_plural = 'Bank Account Balances'

    def __str__(self):
        return f"{self.account.name}: {self.balance_amount} {self.account.currency}"


class DebitCard(BaseAccount):
    """
    Debit card model linked to a bank account.
    """

    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('rupay', 'RuPay'),
        ('amex', 'American Express'),
        ('other', 'Other'),
    ]

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='debit_cards',
        help_text="Linked bank account"
    )

    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        default='visa',
        help_text="Type of card"
    )

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
        null=True,
        blank=True,
        help_text="Card CVV/CVV2 (encrypted)"
    )

    expiry_date = models.DateField(
        help_text="Card expiry date"
    )

    class Meta:
        db_table = 'debit_cards'
        verbose_name = 'Debit Card'
        verbose_name_plural = 'Debit Cards'
        unique_together = [['user', 'bank_account', 'card_number_last4']]

    def __str__(self):
        return f"{self.name} ({self.get_card_type_display()} ****{self.card_number_last4})"

    def clean(self):
        """Validate debit card data"""
        super().clean()

        # Validate card number (basic check - should be digits only)
        if self.card_number:
            clean_number = str(self.card_number).replace(' ', '').replace('-', '')
            if not clean_number.isdigit():
                raise ValidationError({
                    'card_number': 'Card number must contain only digits'
                })
            # Typical length check
            if len(clean_number) < 12 or len(clean_number) > 19:
                raise ValidationError({
                    'card_number': 'Card number must be between 12 and 19 digits'
                })

        # Validate CVV if provided
        if self.cvv:
            clean_cvv = str(self.cvv).strip()
            if not clean_cvv.isdigit():
                raise ValidationError({'cvv': 'CVV must contain only digits'})
            if len(clean_cvv) < 3 or len(clean_cvv) > 4:
                raise ValidationError({'cvv': 'CVV must be 3 or 4 digits'})

    def save(self, *args, **kwargs):
        """Override save to auto-extract last 4 digits and ensure user matches bank account"""
        if self.bank_account:
            self.user = self.bank_account.user

        if self.card_number:
            clean_number = str(self.card_number).replace(' ', '').replace('-', '')
            if len(clean_number) >= 4:
                self.card_number_last4 = clean_number[-4:]
            else:
                self.card_number_last4 = clean_number

        self.full_clean()
        super().save(*args, **kwargs)

    def get_masked_card_number(self):
        """Returns masked card number (e.g., '****1234')"""
        if self.card_number_last4:
            return f"****{self.card_number_last4}"
        return "N/A"

    def get_current_balance(self):
        """Debit card balance is the same as the linked bank account balance."""
        return self.bank_account.get_current_balance()
