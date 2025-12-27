import pytest
from accounts.forms import BankAccountForm
from decimal import Decimal

@pytest.mark.django_db
class TestBankAccountForm:
    def test_form_valid_data(self):
        form_data = {
            'name': 'Test Account',
            'account_type': 'savings',
            'institution': 'Test Bank',
            'opening_balance': Decimal('1000.00'),
            'status': 'active'
        }
        form = BankAccountForm(data=form_data)
        assert form.is_valid()

    def test_form_invalid_ifsc(self):
        form_data = {
            'name': 'Test Account',
            'account_type': 'savings',
            'opening_balance': Decimal('1000.00'),
            'status': 'active',
            'ifsc_code': 'invalid'
        }
        form = BankAccountForm(data=form_data)
        assert form.is_valid() is False
        assert 'ifsc_code' in form.errors
        
    def test_ifsc_uppercasing(self):
        form_data = {
            'name': 'Test Account',
            'account_type': 'savings',
            'opening_balance': Decimal('1000.00'),
            'status': 'active',
            'ifsc_code': 'sbin0001234'
        }
        form = BankAccountForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['ifsc_code'] == 'SBIN0001234'

    def test_required_fields(self):
        form = BankAccountForm(data={})
        assert form.is_valid() is False
        assert 'name' in form.errors
        assert 'account_type' in form.errors
        assert 'opening_balance' in form.errors
