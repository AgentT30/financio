import pytest
from django.utils import timezone
from decimal import Decimal
from transactions.forms import TransactionForm
from categories.models import Category
from accounts.models import BankAccount

@pytest.mark.django_db
class TestTransactionForm:
    def test_form_valid_data(self, test_user, bank_account):
        category = Category.objects.create(user=test_user, name='Food', type='expense')
        form_data = {
            'transaction_type': 'expense',
            'amount': Decimal('50.00'),
            'method_type': 'upi',
            'purpose': 'Lunch',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat(),
            'time': '12:00'
        }
        form = TransactionForm(data=form_data, user=test_user)
        assert form.is_valid()
        assert form.cleaned_data['datetime_ist'].hour == 12

    def test_insufficient_balance_validation(self, test_user, bank_account):
        # bank_account has 1000.00 opening balance from fixture
        category = Category.objects.create(user=test_user, name='Luxury', type='expense')
        form_data = {
            'transaction_type': 'expense',
            'amount': Decimal('2000.00'), # More than balance
            'method_type': 'upi',
            'purpose': 'Expensive item',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        }
        form = TransactionForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'amount' in form.errors
        assert 'Insufficient balance' in form.errors['amount'][0]

    def test_credit_card_balance_exemption(self, test_user, credit_card):
        category = Category.objects.create(user=test_user, name='Shopping', type='expense')
        form_data = {
            'transaction_type': 'expense',
            'amount': Decimal('1000.00'), # Should be fine even if "balance" is 0
            'method_type': 'card',
            'purpose': 'Shopping',
            'category': category.id,
            'account': f"{credit_card.id}|creditcard",
            'date': timezone.now().date().isoformat()
        }
        form = TransactionForm(data=form_data, user=test_user)
        assert form.is_valid() # Credit cards are exempt from balance check in form
