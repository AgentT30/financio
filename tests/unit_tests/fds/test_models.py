import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from fds.models import FixedDeposit

@pytest.mark.django_db
class TestFixedDepositModel:
    def test_fd_creation(self, test_user):
        fd = FixedDeposit.objects.create(
            user=test_user,
            name='HDFC FD',
            institution='HDFC Bank',
            principal_amount=Decimal('100000.00'),
            interest_rate=Decimal('6.50'),
            maturity_amount=Decimal('135000.00'),
            tenure_months=60,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=1825),
            status='active'
        )
        assert str(fd) == 'HDFC FD (HDFC Bank)'
        assert fd.get_interest_earned() == Decimal('35000.00')
        assert not fd.is_matured()

    def test_principal_amount_validation(self, test_user):
        fd = FixedDeposit(
            user=test_user,
            name='Test',
            institution='Bank',
            principal_amount=Decimal('-100.00'), # Invalid
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('100.00'),
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365)
        )
        with pytest.raises(ValidationError) as excinfo:
            fd.full_clean()
        assert 'principal_amount' in excinfo.value.message_dict

    def test_maturity_amount_validation(self, test_user):
        fd = FixedDeposit(
            user=test_user,
            name='Test',
            institution='Bank',
            principal_amount=Decimal('1000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('900.00'), # Less than principal
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365)
        )
        with pytest.raises(ValidationError) as excinfo:
            fd.full_clean()
        assert 'maturity_amount' in excinfo.value.message_dict

    def test_date_validation(self, test_user):
        fd = FixedDeposit(
            user=test_user,
            name='Test',
            institution='Bank',
            principal_amount=Decimal('1000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('1100.00'),
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() - timedelta(days=1) # Before opening
        )
        with pytest.raises(ValidationError) as excinfo:
            fd.full_clean()
        assert 'maturity_date' in excinfo.value.message_dict

    def test_is_matured(self, test_user):
        fd = FixedDeposit.objects.create(
            user=test_user,
            name='Matured FD',
            institution='Bank',
            principal_amount=Decimal('1000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('1100.00'),
            tenure_months=12,
            opened_on=date.today() - timedelta(days=400),
            maturity_date=date.today() - timedelta(days=35),
            status='active'
        )
        assert fd.is_matured()
        assert fd.days_to_maturity() == -35
        badge = fd.get_maturity_badge_info()
        assert badge['type'] == 'matured'
        assert '35 days ago' in badge['text']
