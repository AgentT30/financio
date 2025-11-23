from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from decimal import Decimal


class ControlAccount(models.Model):
    """
    Synthetic ledger accounts for double-entry bookkeeping.
    Represents the "other side" of user transactions.
    Only 2 instances: Income Control, Expense Control.
    """
    
    CONTROL_TYPE_CHOICES = [
        ('income', 'Income Control'),
        ('expense', 'Expense Control'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Control account name"
    )
    account_type = models.CharField(
        max_length=20,
        choices=CONTROL_TYPE_CHOICES,
        unique=True,
        help_text="Type of control account"
    )
    description = models.TextField(
        help_text="Description of this control account"
    )
    
    class Meta:
        db_table = 'control_accounts'
        verbose_name = 'Control Account'
        verbose_name_plural = 'Control Accounts'
    
    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    """
    Journal Entry - represents a complete accounting transaction.
    Contains 2+ postings that must sum to zero (double-entry).
    """
    
    # User who owns this entry
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journal_entries',
        db_index=True,
        help_text="Owner of the journal entry"
    )
    
    # When the transaction occurred (IST)
    occurred_at = models.DateTimeField(
        db_index=True,
        help_text="When the financial event occurred (IST)"
    )
    
    # Description/memo
    memo = models.TextField(
        help_text="Description of the transaction"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this entry was recorded (IST)"
    )
    
    class Meta:
        db_table = 'journal_entries'
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['user', 'occurred_at'], name='idx_journal_user_time'),
        ]
    
    def __str__(self):
        return f"JE-{self.id}: {self.memo[:50]} ({self.occurred_at.strftime('%Y-%m-%d %H:%M')})"
    
    def validate_balanced(self):
        """
        Validate that all postings sum to zero.
        Should be called after all postings are created.
        """
        total = self.postings.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        if total != Decimal('0.00'):
            raise ValidationError(
                f"Journal entry postings must sum to zero. Current sum: {total}"
            )
    
    def get_total_debit(self):
        """Get sum of all debit postings"""
        return self.postings.filter(
            posting_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    
    def get_total_credit(self):
        """Get sum of all credit postings (absolute value)"""
        return abs(self.postings.filter(
            posting_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00'))


class Posting(models.Model):
    """
    Posting - individual debit or credit entry within a journal entry.
    Uses GenericForeignKey to reference any account type (BankAccount, ControlAccount, etc.).
    """
    
    POSTING_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    
    # Parent journal entry
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='postings',
        db_index=True,
        help_text="Parent journal entry"
    )
    
    # Account reference (GenericForeignKey for polymorphism)
    account_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        help_text="Type of account (BankAccount, ControlAccount, etc.)"
    )
    account_object_id = models.PositiveIntegerField(
        help_text="ID of the account"
    )
    account = GenericForeignKey('account_content_type', 'account_object_id')
    
    # Amount (signed: positive for debit, negative for credit)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Signed amount (+ for debit, - for credit)"
    )
    
    # Posting type (for clarity and reporting)
    posting_type = models.CharField(
        max_length=10,
        choices=POSTING_TYPE_CHOICES,
        db_index=True,
        help_text="Debit or Credit"
    )
    
    # Currency (fixed to INR for V1)
    currency = models.CharField(
        max_length=3,
        default='INR',
        help_text="Currency code"
    )
    
    # Optional memo (can override journal entry memo)
    memo = models.TextField(
        null=True,
        blank=True,
        help_text="Optional posting-specific memo"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When posting was created (IST)"
    )
    
    class Meta:
        db_table = 'postings'
        verbose_name = 'Posting'
        verbose_name_plural = 'Postings'
        ordering = ['journal_entry', 'posting_type']
        indexes = [
            models.Index(fields=['journal_entry'], name='idx_posting_journal'),
            models.Index(fields=['account_content_type', 'account_object_id'], name='idx_posting_account'),
        ]
    
    def __str__(self):
        account_str = f"{self.account}" if self.account else f"CT#{self.account_content_type_id}/ID#{self.account_object_id}"
        return f"{self.get_posting_type_display()}: ₹{abs(self.amount)} - {account_str}"
    
    def clean(self):
        """Validate posting data"""
        # Ensure amount sign matches posting type
        if self.posting_type == 'debit' and self.amount < 0:
            raise ValidationError("Debit amount must be positive")
        if self.posting_type == 'credit' and self.amount > 0:
            raise ValidationError("Credit amount must be negative")
        
        # Validate currency
        if self.currency != 'INR':
            raise ValidationError("Only INR currency is supported in V1")
    
    def save(self, *args, **kwargs):
        """Override save to enforce amount sign convention"""
        # Normalize amount based on posting type
        if self.posting_type == 'debit':
            self.amount = abs(self.amount)
        elif self.posting_type == 'credit':
            self.amount = -abs(self.amount)
        
        # Run validation
        self.full_clean()
        super().save(*args, **kwargs)
