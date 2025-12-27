import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from transactions.models import Transaction
from categories.models import Category
from django.contrib.contenttypes.models import ContentType

@pytest.mark.django_db
class TestTransactionModel:
    def test_transaction_creation(self, test_user, bank_account):
        category = Category.objects.create(user=test_user, name='Salary', type='income')
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        
        transaction = Transaction.objects.create(
            user=test_user,
            datetime_ist=timezone.now(),
            transaction_type='income',
            amount=Decimal('5000.00'),
            account_content_type=ct,
            account_object_id=bank_account.id,
            method_type='imps_neft_rtgs',
            purpose='Monthly Salary',
            category=category
        )
        assert transaction.amount == Decimal('5000.00')
        assert not transaction.is_deleted

    def test_amount_validation(self, test_user, bank_account):
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        transaction = Transaction(
            user=test_user,
            datetime_ist=timezone.now(),
            transaction_type='income',
            amount=Decimal('-10.00'),
            account_content_type=ct,
            account_object_id=bank_account.id,
            method_type='cash',
            purpose='Test'
        )
        with pytest.raises(ValidationError) as excinfo:
            transaction.clean()
        assert 'amount' in excinfo.value.message_dict

    def test_category_type_mismatch(self, test_user, bank_account):
        income_cat = Category.objects.create(user=test_user, name='Salary', type='income')
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        
        transaction = Transaction(
            user=test_user,
            datetime_ist=timezone.now(),
            transaction_type='expense', # Mismatch with income category
            amount=Decimal('100.00'),
            account_content_type=ct,
            account_object_id=bank_account.id,
            method_type='cash',
            purpose='Test',
            category=income_cat
        )
        with pytest.raises(ValidationError) as excinfo:
            transaction.clean()
        assert 'category' in excinfo.value.message_dict

    def test_soft_delete(self, test_user, bank_account):
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        transaction = Transaction.objects.create(
            user=test_user,
            datetime_ist=timezone.now(),
            transaction_type='income',
            amount=Decimal('100.00'),
            account_content_type=ct,
            account_object_id=bank_account.id,
            method_type='cash',
            purpose='Test'
        )
        transaction.delete()
        assert transaction.is_deleted
        assert transaction.deleted_at is not None
        
        # Verify it's still in DB but marked deleted
        assert Transaction.objects.filter(pk=transaction.pk).exists()
