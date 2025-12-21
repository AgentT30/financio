import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from ledger.models import ControlAccount, JournalEntry, Posting
from django.contrib.contenttypes.models import ContentType

@pytest.mark.django_db
class TestLedgerModels:
    def test_control_account_creation(self):
        # Clear existing control accounts created by autouse fixture
        ControlAccount.objects.all().delete()
        ca = ControlAccount.objects.create(
            name='Test Income',
            account_type='income',
            description='Test'
        )
        assert str(ca) == 'Test Income'

    def test_journal_entry_balanced_validation(self, test_user, bank_account):
        je = JournalEntry.objects.create(
            user=test_user,
            occurred_at=timezone.now(),
            memo='Test Entry'
        )
        bank_ct = ContentType.objects.get_for_model(bank_account.__class__)
        
        # Unbalanced entry
        Posting.objects.create(
            journal_entry=je,
            account_content_type=bank_ct,
            account_object_id=bank_account.id,
            amount=Decimal('100.00'),
            posting_type='debit'
        )
        
        with pytest.raises(ValidationError) as excinfo:
            je.validate_balanced()
        assert 'must sum to zero' in str(excinfo.value)
        
        # Balance it
        Posting.objects.create(
            journal_entry=je,
            account_content_type=bank_ct,
            account_object_id=bank_account.id,
            amount=Decimal('-100.00'),
            posting_type='credit'
        )
        je.validate_balanced() # Should not raise

    def test_posting_sign_normalization(self, test_user, bank_account):
        je = JournalEntry.objects.create(
            user=test_user,
            occurred_at=timezone.now(),
            memo='Test'
        )
        bank_ct = ContentType.objects.get_for_model(bank_account.__class__)
        
        # Debit should be positive
        p1 = Posting.objects.create(
            journal_entry=je,
            account_content_type=bank_ct,
            account_object_id=bank_account.id,
            amount=Decimal('-50.00'), # Wrong sign
            posting_type='debit'
        )
        assert p1.amount == Decimal('50.00')
        
        # Credit should be negative
        p2 = Posting.objects.create(
            journal_entry=je,
            account_content_type=bank_ct,
            account_object_id=bank_account.id,
            amount=Decimal('50.00'), # Wrong sign
            posting_type='credit'
        )
        assert p2.amount == Decimal('-50.00')
