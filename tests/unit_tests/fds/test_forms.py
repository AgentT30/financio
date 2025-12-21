import pytest
from datetime import date, timedelta
from decimal import Decimal
from fds.forms import FixedDepositForm

@pytest.mark.django_db
class TestFixedDepositForm:
    def test_form_valid_data(self):
        form_data = {
            'name': 'HDFC FD',
            'institution': 'HDFC Bank',
            'principal_amount': Decimal('100000.00'),
            'interest_rate': Decimal('6.50'),
            'maturity_amount': Decimal('135000.00'),
            'tenure_months': 60,
            'opened_on': date.today().isoformat(),
            'maturity_date': (date.today() + timedelta(days=1825)).isoformat(),
            'status': 'active',
            'compounding_frequency': 'quarterly'
        }
        form = FixedDepositForm(data=form_data)
        assert form.is_valid()

    def test_form_invalid_dates(self):
        form_data = {
            'name': 'HDFC FD',
            'institution': 'HDFC Bank',
            'principal_amount': Decimal('100000.00'),
            'interest_rate': Decimal('6.50'),
            'maturity_amount': Decimal('135000.00'),
            'tenure_months': 60,
            'opened_on': date.today().isoformat(),
            'maturity_date': (date.today() - timedelta(days=1)).isoformat(), # Invalid
            'status': 'active'
        }
        form = FixedDepositForm(data=form_data)
        assert not form.is_valid()
        assert 'maturity_date' in form.errors

    def test_form_maturity_less_than_principal(self):
        form_data = {
            'name': 'HDFC FD',
            'institution': 'HDFC Bank',
            'principal_amount': Decimal('100000.00'),
            'interest_rate': Decimal('6.50'),
            'maturity_amount': Decimal('90000.00'), # Invalid
            'tenure_months': 60,
            'opened_on': date.today().isoformat(),
            'maturity_date': (date.today() + timedelta(days=1825)).isoformat(),
            'status': 'active'
        }
        form = FixedDepositForm(data=form_data)
        assert not form.is_valid()
        assert 'maturity_amount' in form.errors
