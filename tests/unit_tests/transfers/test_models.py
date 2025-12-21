import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from transfers.models import Transfer
from django.contrib.contenttypes.models import ContentType

@pytest.mark.django_db
class TestTransferModel:
    def test_transfer_creation(self, test_user, bank_account, credit_card):
        from_ct = ContentType.objects.get_for_model(bank_account.__class__)
        to_ct = ContentType.objects.get_for_model(credit_card.__class__)
        
        transfer = Transfer.objects.create(
            user=test_user,
            datetime_ist=timezone.now(),
            amount=Decimal('500.00'),
            from_account_content_type=from_ct,
            from_account_object_id=bank_account.id,
            to_account_content_type=to_ct,
            to_account_object_id=credit_card.id,
            method_type='upi',
            memo='Test Transfer'
        )
        assert transfer.amount == Decimal('500.00')
        assert not transfer.is_deleted()

    def test_same_account_validation(self, test_user, bank_account):
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        transfer = Transfer(
            user=test_user,
            datetime_ist=timezone.now(),
            amount=Decimal('100.00'),
            from_account_content_type=ct,
            from_account_object_id=bank_account.id,
            to_account_content_type=ct,
            to_account_object_id=bank_account.id,
            method_type='upi',
            memo='Self Transfer'
        )
        with pytest.raises(ValidationError) as excinfo:
            transfer.clean()
        assert 'Cannot transfer to the same account' in str(excinfo.value)

    def test_negative_amount_validation(self, test_user, bank_account, credit_card):
        from_ct = ContentType.objects.get_for_model(bank_account.__class__)
        to_ct = ContentType.objects.get_for_model(credit_card.__class__)
        
        transfer = Transfer(
            user=test_user,
            datetime_ist=timezone.now(),
            amount=Decimal('-100.00'),
            from_account_content_type=from_ct,
            from_account_object_id=bank_account.id,
            to_account_content_type=to_ct,
            to_account_object_id=credit_card.id,
            method_type='upi',
            memo='Negative Transfer'
        )
        with pytest.raises(ValidationError) as excinfo:
            transfer.clean()
        assert 'Transfer amount must be positive' in str(excinfo.value)

    def test_soft_delete(self, test_user, bank_account, credit_card):
        from_ct = ContentType.objects.get_for_model(bank_account.__class__)
        to_ct = ContentType.objects.get_for_model(credit_card.__class__)
        
        transfer = Transfer.objects.create(
            user=test_user,
            datetime_ist=timezone.now(),
            amount=Decimal('100.00'),
            from_account_content_type=from_ct,
            from_account_object_id=bank_account.id,
            to_account_content_type=to_ct,
            to_account_object_id=credit_card.id,
            method_type='upi',
            memo='Test'
        )
        transfer.soft_delete()
        assert transfer.is_deleted()
        assert transfer.deleted_at is not None
