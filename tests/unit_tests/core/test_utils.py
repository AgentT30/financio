import pytest
from core.utils import get_all_accounts_with_emoji, get_account_from_compound_value, get_account_choices_for_form
from accounts.models import BankAccount
from creditcards.models import CreditCard
from decimal import Decimal

from datetime import date, timedelta

@pytest.mark.django_db
class TestCoreUtils:
    def test_get_all_accounts_with_emoji(self, test_user):
        # Create a bank account
        bank = BankAccount.objects.create(
            user=test_user,
            name='HDFC Savings',
            institution='HDFC Bank',
            status='active'
        )
        # Create a credit card
        card = CreditCard.objects.create(
            user=test_user,
            name='ICICI Amazon',
            institution='ICICI Bank',
            card_number='1234567890123456',
            cvv='123',
            credit_limit=Decimal('50000.00'),
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            status='active'
        )
        
        accounts = get_all_accounts_with_emoji(test_user)
        assert len(accounts) == 2
        
        # Check bank account entry
        bank_entry = next(a for a in accounts if a[2] == f"{bank.id}|bankaccount")
        assert "🏦 HDFC Savings" in bank_entry[1]
        
        # Check credit card entry
        card_entry = next(a for a in accounts if a[2] == f"{card.id}|creditcard")
        assert "💳 ICICI Amazon" in card_entry[1]

    def test_get_account_from_compound_value(self, test_user):
        bank = BankAccount.objects.create(user=test_user, name='Bank', status='active')
        
        # Valid bank account
        compound = f"{bank.id}|bankaccount"
        obj = get_account_from_compound_value(compound, test_user)
        assert obj == bank
        
        # Invalid format
        with pytest.raises(ValueError, match="Invalid account value format"):
            get_account_from_compound_value("invalid", test_user)
            
        # Unknown type
        with pytest.raises(ValueError, match="Unknown account type"):
            get_account_from_compound_value("1|unknown", test_user)
            
        # Non-existent ID
        with pytest.raises(ValueError, match="not found"):
            get_account_from_compound_value("999|bankaccount", test_user)

    def test_get_account_choices_for_form(self, test_user):
        BankAccount.objects.create(user=test_user, name='Bank', institution='SBI', status='active')
        choices = get_account_choices_for_form(test_user)
        assert len(choices) == 1
        assert isinstance(choices[0], tuple)
        assert '|bankaccount' in choices[0][0]
        assert '🏦 Bank' in choices[0][1]
