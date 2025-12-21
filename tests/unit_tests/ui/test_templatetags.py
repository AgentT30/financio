import pytest
from decimal import Decimal
from core.templatetags.indian_numbers import indian_format
from transactions.templatetags.transaction_tags import ordinal, get_account
from accounts.models import BankAccount
from django.contrib.contenttypes.models import ContentType

class TestIndianNumbersFilter:
    def test_indian_format_basic(self):
        assert indian_format(1000) == '1,000.00'
        assert indian_format(10000) == '10,000.00'
        assert indian_format(100000) == '1,00,000.00'
        assert indian_format(1000000) == '10,00,000.00'
        assert indian_format(10000000) == '1,00,00,000.00'

    def test_indian_format_decimals(self):
        assert indian_format(1234.567, decimals=2) == '1,234.57'
        assert indian_format(1234.5, decimals=2) == '1,234.50'
        assert indian_format(1234, decimals=0) == '1,234'
        assert indian_format(100000, decimals=0) == '1,00,000'

    def test_indian_format_negative(self):
        assert indian_format(-1000) == '-1,000.00'
        assert indian_format(-100000) == '-1,00,000.00'

    def test_indian_format_edge_cases(self):
        assert indian_format(0) == '0.00'
        assert indian_format(None) == ''
        assert indian_format('not a number') == 'not a number'

class TestTransactionTags:
    def test_ordinal_filter(self):
        assert ordinal(1) == '1st'
        assert ordinal(2) == '2nd'
        assert ordinal(3) == '3rd'
        assert ordinal(4) == '4th'
        assert ordinal(11) == '11th'
        assert ordinal(12) == '12th'
        assert ordinal(13) == '13th'
        assert ordinal(21) == '21st'
        assert ordinal(22) == '22nd'
        assert ordinal(23) == '23rd'
        assert ordinal('invalid') == 'invalid'

    @pytest.mark.django_db
    def test_get_account_filter(self, test_user):
        account = BankAccount.objects.create(
            user=test_user,
            name='My Savings',
            institution='SBI',
            account_type='savings'
        )
        
        # Mock a transaction-like object
        class MockTransaction:
            def __init__(self, obj):
                self.account_content_type = ContentType.objects.get_for_model(obj)
                self.account_object_id = obj.id
        
        txn = MockTransaction(account)
        assert get_account(txn) == '🏦 My Savings'

    def test_get_account_filter_unknown(self):
        class MockTransaction:
            account_content_type = None
            account_object_id = None
            
        assert get_account(MockTransaction()) == 'Unknown'
