import pytest
from django.core.exceptions import ValidationError
from accounts.models import BankAccount
from decimal import Decimal

@pytest.mark.django_db
class TestBaseAccountModel:
    """
    Tests for BaseAccount abstract model using BankAccount as a concrete implementation.
    """
    def test_base_account_common_fields(self, test_user):
        account = BankAccount.objects.create(
            user=test_user,
            name='Test Account',
            account_type='savings',
            opening_balance=Decimal('100.00'),
            currency='INR',
            status='active',
            color='#3B82F6'
        )
        assert account.user == test_user
        assert account.name == 'Test Account'
        assert account.currency == 'INR'
        assert account.status == 'active'
        assert account.color == '#3B82F6'

    def test_currency_validation(self, test_user):
        account = BankAccount(
            user=test_user,
            name='USD Account',
            account_type='savings',
            currency='USD' # Only INR supported
        )
        with pytest.raises(ValidationError) as excinfo:
            account.full_clean()
        assert 'currency' in excinfo.value.message_dict

    def test_color_validation(self, test_user):
        account = BankAccount(
            user=test_user,
            name='Bad Color',
            account_type='savings',
            color='invalid' # Not a hex code
        )
        with pytest.raises(ValidationError) as excinfo:
            account.full_clean()
        assert 'color' in excinfo.value.message_dict

    def test_archive_activate(self, test_user):
        account = BankAccount.objects.create(
            user=test_user,
            name='Archive Test',
            account_type='savings'
        )
        assert account.status == 'active'
        
        account.archive()
        account.refresh_from_db()
        assert account.status == 'archived'
        
        account.activate()
        account.refresh_from_db()
        assert account.status == 'active'
