import pytest
from django.core.exceptions import ValidationError
from accounts.models import BankAccount, BankAccountBalance
from transactions.models import Transaction
from transfers.models import Transfer
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

@pytest.mark.django_db
class TestBankAccountModel:
    def test_account_creation(self, test_user):
        account = BankAccount.objects.create(
            user=test_user,
            name='HDFC Savings',
            account_type='savings',
            institution='HDFC Bank',
            account_number='1234567890',
            opening_balance=Decimal('5000.00')
        )
        assert account.name == 'HDFC Savings'
        assert account.account_number_last4 == '7890'
        assert str(account) == 'HDFC Savings (Savings Account)'

    def test_ifsc_validation(self, test_user):
        account = BankAccount(
            user=test_user,
            name='Test',
            ifsc_code='INVALID123'
        )
        with pytest.raises(ValidationError):
            account.clean()

        account.ifsc_code = 'HDFC0001234'
        account.clean()  # Should not raise

    def test_masked_account_number(self, test_user):
        account = BankAccount(user=test_user, name='Test', account_number='1234567890')
        account.save()
        assert account.get_masked_account_number() == '****7890'

        account.account_number = None
        account.save()
        assert account.get_masked_account_number() == 'N/A'

    def test_get_current_balance(self, bank_account):
        assert bank_account.get_current_balance() == Decimal('1000.00')
        
        # Test fallback
        bank_account.balance.delete()
        assert bank_account.get_current_balance() == Decimal('1000.00')

    def test_can_delete(self, bank_account, test_user):
        assert bank_account.can_delete() is True

        # Add transaction
        from django.utils import timezone
        ct = ContentType.objects.get_for_model(BankAccount)
        Transaction.objects.create(
            user=test_user,
            account_content_type=ct,
            account_object_id=bank_account.id,
            amount=Decimal('100.00'),
            transaction_type='expense',
            datetime_ist=timezone.now(),
            method_type='upi',
            purpose='Test transaction'
        )
        assert bank_account.can_delete() is False

    def test_archive_activate(self, bank_account):
        bank_account.archive()
        assert bank_account.status == 'archived'
        bank_account.activate()
        assert bank_account.status == 'active'
