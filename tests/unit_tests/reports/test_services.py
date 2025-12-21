import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from reports.services import ReportService
from transactions.models import Transaction
from categories.models import Category
from accounts.models import BankAccount
from fds.models import FixedDeposit
from investments.models import Investment, InvestmentTransaction
from ledger.models import JournalEntry, Posting
from django.contrib.contenttypes.models import ContentType

@pytest.mark.django_db
class TestReportService:
    def test_get_monthly_cashflow(self, test_user):
        # Create categories
        income_cat = Category.objects.create(user=test_user, name='Salary', type='income')
        expense_cat = Category.objects.create(user=test_user, name='Rent', type='expense')
        
        # Create bank account
        bank = BankAccount.objects.create(user=test_user, name='Bank', institution='SBI', status='active')
        ct = ContentType.objects.get_for_model(bank)
        
        # Create transactions for current month and last month
        now = timezone.now()
        last_month = now - timedelta(days=30)
        
        # Current month
        Transaction.objects.create(
            user=test_user,
            datetime_ist=now,
            transaction_type='income',
            amount=Decimal('5000.00'),
            category=income_cat,
            account_content_type=ct,
            account_object_id=bank.id,
            method_type='upi',
            purpose='Salary'
        )
        Transaction.objects.create(
            user=test_user,
            datetime_ist=now,
            transaction_type='expense',
            amount=Decimal('2000.00'),
            category=expense_cat,
            account_content_type=ct,
            account_object_id=bank.id,
            method_type='card',
            purpose='Rent'
        )
        
        # Last month
        Transaction.objects.create(
            user=test_user,
            datetime_ist=last_month,
            transaction_type='income',
            amount=Decimal('4000.00'),
            category=income_cat,
            account_content_type=ct,
            account_object_id=bank.id,
            method_type='upi',
            purpose='Bonus'
        )
        
        report = ReportService.get_monthly_cashflow(test_user, months_count=2)
        
        assert len(report['labels']) == 2
        assert report['income'][-1] == 5000.0
        assert report['expense'][-1] == 2000.0
        assert report['income'][-2] == 4000.0
        assert report['expense'][-2] == 0.0

    def test_get_expense_breakdown(self, test_user):
        expense_cat1 = Category.objects.create(user=test_user, name='Food', type='expense', color='#FF0000')
        expense_cat2 = Category.objects.create(user=test_user, name='Travel', type='expense', color='#00FF00')
        
        bank = BankAccount.objects.create(user=test_user, name='Bank', institution='SBI', status='active')
        ct = ContentType.objects.get_for_model(bank)
        
        now = timezone.now()
        Transaction.objects.create(
            user=test_user,
            datetime_ist=now,
            transaction_type='expense',
            amount=Decimal('500.00'),
            category=expense_cat1,
            account_content_type=ct,
            account_object_id=bank.id,
            method_type='upi',
            purpose='Lunch'
        )
        Transaction.objects.create(
            user=test_user,
            datetime_ist=now,
            transaction_type='expense',
            amount=Decimal('300.00'),
            category=expense_cat2,
            account_content_type=ct,
            account_object_id=bank.id,
            method_type='cash',
            purpose='Bus'
        )
        
        report = ReportService.get_expense_breakdown(test_user)
        
        assert 'Food' in report['labels']
        assert 'Travel' in report['labels']
        assert 500.0 in report['data']
        assert 300.0 in report['data']
        assert '#FF0000' in report['colors']
        assert '#00FF00' in report['colors']

    def test_get_net_worth_trend(self, test_user):
        # 1. Bank Account with Opening Balance and Postings
        bank = BankAccount.objects.create(
            user=test_user, 
            name='Bank', 
            institution='SBI',
            opening_balance=Decimal('1000.00'),
            status='active'
        )
        ct_bank = ContentType.objects.get_for_model(bank)
        
        # Create a posting (Debit increases bank balance)
        je = JournalEntry.objects.create(user=test_user, occurred_at=timezone.now(), memo='Test JE')
        Posting.objects.create(
            journal_entry=je,
            account_content_type=ct_bank,
            account_object_id=bank.id,
            amount=Decimal('500.00'),
            posting_type='debit'
        )
        
        # 2. Fixed Deposit
        FixedDeposit.objects.create(
            user=test_user,
            name='FD 1',
            institution='HDFC Bank',
            principal_amount=Decimal('5000.00'),
            interest_rate=Decimal('7.50'),
            maturity_amount=Decimal('5500.00'),
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365),
            status='active'
        )
        
        # 3. Investment
        from investments.models import Broker
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        inv = Investment.objects.create(
            user=test_user,
            broker=broker,
            name='Stock',
            current_price=Decimal('100.00'),
            status='active'
        )
        InvestmentTransaction.objects.create(
            investment=inv,
            transaction_type='buy',
            quantity=Decimal('10'),
            price_per_unit=Decimal('90.00'),
            total_amount=Decimal('900.00')
        )
        
        # Current Net Worth = Bank (1000 + 500) + FD (5500) + Investment (10 * 100) = 1500 + 5500 + 1000 = 8000
        report = ReportService.get_net_worth_trend(test_user, months_count=1)
        
        assert report['data'][0] == 8000.0
