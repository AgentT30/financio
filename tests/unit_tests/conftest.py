import pytest
from django.contrib.auth.models import User
from accounts.models import BankAccount, BankAccountBalance
from decimal import Decimal

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser', password='FinancioTest@2025')

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='otheruser', password='FinancioTest@2025')

@pytest.fixture
def bank_account(test_user):
    from accounts.models import BankAccount, BankAccountBalance
    account = BankAccount.objects.create(
        user=test_user,
        name='Test Bank',
        account_type='savings',
        opening_balance=Decimal('1000.00'),
        status='active'
    )
    BankAccountBalance.objects.create(account=account, balance_amount=Decimal('1000.00'))
    return account

@pytest.fixture
def credit_card(test_user):
    from creditcards.models import CreditCard, CreditCardBalance
    from datetime import date, timedelta
    card = CreditCard.objects.create(
        user=test_user,
        name='Test Card',
        institution='Test Bank',
        card_number='1234567890123',
        cvv='123',
        billing_day=1,
        due_day=20,
        expiry_date=date.today() + timedelta(days=365),
        credit_limit=Decimal('50000.00'),
        opening_balance=Decimal('0.00'),
        status='active'
    )
    CreditCardBalance.objects.create(account=card, balance_amount=Decimal('0.00'))
    return card

@pytest.fixture(autouse=True)
def control_accounts(db):
    from ledger.models import ControlAccount
    income_control, _ = ControlAccount.objects.get_or_create(
        account_type='income',
        defaults={'name': 'Income Control', 'description': 'Synthetic account for income'}
    )
    expense_control, _ = ControlAccount.objects.get_or_create(
        account_type='expense',
        defaults={'name': 'Expense Control', 'description': 'Synthetic account for expenses'}
    )
    return income_control, expense_control
