import pytest
from django.utils import timezone
from decimal import Decimal
from transfers.forms import TransferForm
from accounts.models import BankAccount

@pytest.mark.django_db
class TestTransferForm:
    def test_form_valid_data(self, test_user, bank_account, credit_card):
        form_data = {
            'amount': Decimal('100.00'),
            'method_type': 'upi',
            'memo': 'Test Transfer',
            'from_account': f"{bank_account.id}|bankaccount",
            'to_account': f"{credit_card.id}|creditcard",
            'date': timezone.now().date().isoformat(),
            'time': '10:00'
        }
        form = TransferForm(data=form_data, user=test_user)
        assert form.is_valid()
        assert form.cleaned_data['datetime_ist'].hour == 10

    def test_insufficient_balance_validation(self, test_user, bank_account, credit_card):
        # bank_account has 1000.00
        form_data = {
            'amount': Decimal('2000.00'),
            'method_type': 'upi',
            'memo': 'Too much',
            'from_account': f"{bank_account.id}|bankaccount",
            'to_account': f"{credit_card.id}|creditcard",
            'date': timezone.now().date().isoformat()
        }
        form = TransferForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'Insufficient balance' in str(form.errors['__all__'])

    def test_same_account_validation(self, test_user, bank_account):
        form_data = {
            'amount': Decimal('100.00'),
            'method_type': 'upi',
            'memo': 'Self',
            'from_account': f"{bank_account.id}|bankaccount",
            'to_account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        }
        form = TransferForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'Source and destination accounts must be different' in str(form.errors['__all__'])
