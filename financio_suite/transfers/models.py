from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from ledger.models import JournalEntry


class Transfer(models.Model):
    """
    Money transfer between two accounts.
    Each transfer creates a journal entry with two postings (debit from_account, credit to_account).
    """

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

    # User who owns this transfer
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transfers',
        db_index=True,
        help_text="Owner of the transfer"
    )

    # When transfer occurred (IST)
    datetime_ist = models.DateTimeField(
        db_index=True,
        help_text="Date and time of transfer (IST)"
    )

    # Amount transferred (always positive)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Transfer amount (always positive)"
    )

    # From account (GenericForeignKey - supports BankAccount, CreditCard, Wallet, etc.)
    from_account_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='transfers_from',
        help_text="Content type of source account"
    )
    from_account_object_id = models.PositiveIntegerField(
        help_text="ID of source account"
    )
    from_account = GenericForeignKey('from_account_content_type', 'from_account_object_id')

    # To account (GenericForeignKey - supports BankAccount, CreditCard, Wallet, etc.)
    to_account_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='transfers_to',
        help_text="Content type of destination account"
    )
    to_account_object_id = models.PositiveIntegerField(
        help_text="ID of destination account"
    )
    to_account = GenericForeignKey('to_account_content_type', 'to_account_object_id')

    # Payment method
    method_type = models.CharField(
        max_length=20,
        choices=METHOD_TYPE_CHOICES,
        db_index=True,
        help_text="Method used for transfer"
    )

    # Description/memo
    memo = models.TextField(
        help_text="Transfer description/notes"
    )

    # Link to ledger journal entry
    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.PROTECT,
        related_name='transfer',
        null=True,
        blank=True,
        help_text="Associated journal entry in ledger"
    )

    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Soft delete timestamp"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )

    class Meta:
        db_table = 'transfers'
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
        ordering = ['-datetime_ist']
        indexes = [
            models.Index(fields=['user', 'datetime_ist'], name='idx_transfer_user_date'),
            models.Index(fields=['user', 'deleted_at'], name='idx_transfer_user_deleted'),
        ]

    def __str__(self):
        return f"Transfer: ₹{self.amount} ({self.datetime_ist.strftime('%Y-%m-%d')})"

    def clean(self):
        """Validate transfer constraints"""
        # Amount must be positive
        if self.amount and self.amount <= 0:
            raise ValidationError("Transfer amount must be positive")

        # From and to accounts must be different (compare ContentType ID and object ID)
        if (self.from_account_content_type_id == self.to_account_content_type_id and
            self.from_account_object_id == self.to_account_object_id):
            raise ValidationError("Cannot transfer to the same account")

        # Both accounts must belong to the user (only validate if user is set)
        if self.user_id:  # Check if user is set before validating ownership
            if self.from_account and hasattr(self.from_account, 'user'):
                if self.from_account.user != self.user:
                    raise ValidationError("Source account does not belong to this user")

            if self.to_account and hasattr(self.to_account, 'user'):
                if self.to_account.user != self.user:
                    raise ValidationError("Destination account does not belong to this user")

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        # Only run full_clean if skip_validation is not set
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)

    def soft_delete(self):
        """Soft delete the transfer"""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def is_deleted(self):
        """Check if transfer is soft deleted"""
        return self.deleted_at is not None

