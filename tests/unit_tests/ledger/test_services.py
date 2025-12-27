import pytest
from decimal import Decimal
from django.utils import timezone
from ledger.services import LedgerService
from ledger.models import JournalEntry, Posting
from accounts.models import BankAccountBalance
from transactions.models import Transaction

@pytest.mark.django_db
class TestLedgerService:
    def test_create_simple_entry_income(self, test_user, bank_account):
        service = LedgerService()
        je = service.create_simple_entry(
            user=test_user,
            transaction_type='income',
            account=bank_account,
            amount=Decimal('1000.00'),
            occurred_at=timezone.now(),
            memo='Salary'
        )
        
        assert je.postings.count() == 2
        # Check user account posting (debit)
        user_posting = je.postings.get(account_object_id=bank_account.id)
        assert user_posting.amount == Decimal('1000.00')
        assert user_posting.posting_type == 'debit'
        
        # Check balance update
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('2000.00')

    def test_create_simple_entry_expense(self, test_user, bank_account):
        service = LedgerService()
        je = service.create_simple_entry(
            user=test_user,
            transaction_type='expense',
            account=bank_account,
            amount=Decimal('200.00'),
            occurred_at=timezone.now(),
            memo='Groceries'
        )
        
        # Check user account posting (credit)
        user_posting = je.postings.get(account_object_id=bank_account.id)
        assert user_posting.amount == Decimal('-200.00')
        assert user_posting.posting_type == 'credit'
        
        # Check balance update
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('800.00')

    def test_create_transfer_entry(self, test_user, bank_account, credit_card):
        service = LedgerService()
        je, from_bal, to_bal = service.create_transfer_entry(
            user=test_user,
            occurred_at=timezone.now(),
            amount=Decimal('300.00'),
            from_account=bank_account,
            to_account=credit_card,
            memo='Payment'
        )
        
        assert je.postings.count() == 2
        assert from_bal == Decimal('700.00')
        assert to_bal == Decimal('300.00')

    def test_recalculate_user_balances(self, test_user, bank_account):
        service = LedgerService()
        
        # Create a transaction manually but mess up the balance
        je = service.create_simple_entry(
            user=test_user,
            transaction_type='income',
            account=bank_account,
            amount=Decimal('500.00'),
            occurred_at=timezone.now(),
            memo='Test'
        )
        
        # Manually corrupt balance
        balance = bank_account.balance
        balance.balance_amount = Decimal('0.00')
        balance.save()
        
        # We need a transaction object linked to the journal entry for recalculate to pick it up
        Transaction.objects.create(
            user=test_user,
            datetime_ist=je.occurred_at,
            transaction_type='income',
            amount=Decimal('500.00'),
            journal_entry=je,
            purpose='Test',
            account_content_type=je.postings.first().account_content_type,
            account_object_id=bank_account.id,
            method_type='cash'
        )
        
        results = service.recalculate_user_balances(test_user)
        assert results['banks_fixed'] == 1
        
        bank_account.refresh_from_db()
        # Opening 1000 + 500 = 1500
        assert bank_account.get_current_balance() == Decimal('1500.00')
