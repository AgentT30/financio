from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from categories.models import Category
from ledger.models import JournalEntry


class Transaction(models.Model):
    """
    User-facing transaction model for income/expense tracking.
    Each transaction links to a JournalEntry in the ledger.
    """

    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    METHOD_TYPE_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Debit/Credit Card'),
        ('netbanking', 'Net Banking'),
        ('cash', 'Cash'),
        ('wallet', 'Digital Wallet'),
        ('imps_neft_rtgs', 'IMPS/NEFT/RTGS'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]

    # User who owns this transaction
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        db_index=True,
        help_text="Owner of the transaction"
    )

    # When transaction occurred (IST)
    datetime_ist = models.DateTimeField(
        db_index=True,
        help_text="Date and time of transaction (IST)"
    )

    # Transaction type (income or expense)
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True,
        help_text="Type of transaction"
    )

    # Amount (always positive)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Transaction amount (always positive)"
    )

    # Account reference (GenericForeignKey)
    account_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        help_text="Type of account (BankAccount, CreditCard, etc.)"
    )
    account_object_id = models.PositiveIntegerField(
        help_text="ID of the account"
    )
    account = GenericForeignKey('account_content_type', 'account_object_id')

    # Payment method
    method_type = models.CharField(
        max_length=20,
        choices=METHOD_TYPE_CHOICES,
        db_index=True,
        help_text="Payment method used"
    )

    # Purpose/description
    purpose = models.TextField(
        help_text="Description or purpose of transaction"
    )

    # Category
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='transactions',
        db_index=True,
        null=True,
        blank=True,
        help_text="Transaction category (optional)"
    )

    # Link to journal entry (one-to-one)
    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.PROTECT,
        related_name='transaction',
        null=True,
        blank=True,
        help_text="Linked journal entry in ledger"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When transaction was recorded (IST)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp (IST)"
    )

    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft delete timestamp"
    )

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-datetime_ist']
        indexes = [
            models.Index(fields=['user', 'datetime_ist'], name='idx_txn_user_time'),
            models.Index(fields=['user', 'transaction_type'], name='idx_txn_user_type'),
            models.Index(fields=['category'], name='idx_txn_category'),
            models.Index(fields=['account_content_type', 'account_object_id'], name='idx_txn_account'),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()}: ₹{self.amount} - {self.purpose[:30]} ({self.datetime_ist.strftime('%Y-%m-%d')})"

    def clean(self):
        """Validate transaction data"""
        # Validate amount is positive
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero'})

        # Validate category type matches transaction type
        if self.category:
            if self.transaction_type == 'income' and self.category.type != 'income':
                raise ValidationError({
                    'category': 'Income transaction must use an income category'
                })
            if self.transaction_type == 'expense' and self.category.type != 'expense':
                raise ValidationError({
                    'category': 'Expense transaction must use an expense category'
                })

        # Validate account belongs to user (only if user is already set)
        if self.user_id and self.account and hasattr(self.account, 'user'):
            if self.account.user_id != self.user_id:
                raise ValidationError({
                    'account': 'Account must belong to the transaction owner'
                })

    def save(self, skip_validation=False, *args, **kwargs):
        """Override save to run validation"""
        if not skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Soft delete by setting deleted_at"""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self):
        """Actually delete from database (admin only)"""
        super().delete()

    @property
    def is_deleted(self):
        """Check if transaction is soft-deleted"""
        return self.deleted_at is not None
