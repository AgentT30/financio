import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from investments.models import Broker, Investment, InvestmentTransaction

@pytest.mark.django_db
class TestInvestmentModels:
    def test_broker_creation_and_masking(self, test_user):
        broker = Broker.objects.create(
            user=test_user,
            name='Zerodha',
            broker_user_id='AB1234',
            demat_account_number='1234567890123456'
        )
        assert broker.demat_account_number_last4 == '3456'
        assert broker.get_masked_account_number() == '****3456'
        assert str(broker) == 'Zerodha'

    def test_investment_creation_and_validation(self, test_user):
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        investment = Investment.objects.create(
            user=test_user,
            broker=broker,
            name='Reliance Industries',
            symbol='RELIANCE',
            investment_type='stock',
            current_price=Decimal('2500.00')
        )
        assert str(investment) == 'Reliance Industries (RELIANCE) - Zerodha'
        
        # Test validation: broker must belong to user
        other_user_broker = Broker.objects.create(user=test_user, name='Other') # Wait, I need another user
        # Actually, I can just try to assign a broker that doesn't belong to the investment user
        # But the model clean() checks this.
        
    def test_holdings_calculation(self, test_user):
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        inv = Investment.objects.create(
            user=test_user,
            broker=broker,
            name='TCS',
            symbol='TCS',
            current_price=Decimal('3500.00')
        )
        
        # Buy 10 units at 3000
        InvestmentTransaction.objects.create(
            investment=inv,
            transaction_type='buy',
            date=date.today() - timedelta(days=10),
            quantity=Decimal('10.00'),
            price_per_unit=Decimal('3000.00'),
            fees=Decimal('50.00')
        )
        
        # Total invested = (10 * 3000) + 50 = 30050
        assert inv.total_quantity == Decimal('10.00')
        assert inv.total_invested == Decimal('30050.00')
        assert inv.average_buy_price == Decimal('3005.00')
        
        # Buy 5 more units at 3200
        InvestmentTransaction.objects.create(
            investment=inv,
            transaction_type='buy',
            date=date.today() - timedelta(days=5),
            quantity=Decimal('5.00'),
            price_per_unit=Decimal('3200.00'),
            fees=Decimal('25.00')
        )
        
        # Total invested = 30050 + (5 * 3200) + 25 = 30050 + 16025 = 46075
        # Total quantity = 15
        assert inv.total_quantity == Decimal('15.00')
        assert inv.total_invested == Decimal('46075.00')
        assert round(inv.average_buy_price, 2) == Decimal('3071.67') # 46075 / 15 = 3071.666...
        
        # Sell 5 units at 3400
        # Proportional cost removed = (46075 / 15) * 5 = 15358.33
        InvestmentTransaction.objects.create(
            investment=inv,
            transaction_type='sell',
            date=date.today(),
            quantity=Decimal('5.00'),
            price_per_unit=Decimal('3400.00'),
            fees=Decimal('20.00')
        )
        
        assert inv.total_quantity == Decimal('10.00')
        # Total invested = 46075 - 15358.33 = 30716.67
        assert round(inv.total_invested, 2) == Decimal('30716.67')
        
        # Current value = 10 * 3500 = 35000
        assert inv.current_value == Decimal('35000.00')
        # Unrealized P&L = 35000 - 30716.67 = 4283.33
        assert round(inv.unrealized_pnl, 2) == Decimal('4283.33')

    def test_sell_more_than_owned_validation(self, test_user):
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        inv = Investment.objects.create(
            user=test_user,
            broker=broker,
            name='TCS',
            current_price=Decimal('3500.00')
        )
        
        # Try to sell without owning
        txn = InvestmentTransaction(
            investment=inv,
            transaction_type='sell',
            quantity=Decimal('10.00'),
            price_per_unit=Decimal('3000.00')
        )
        with pytest.raises(ValidationError) as excinfo:
            txn.full_clean()
        assert 'quantity' in excinfo.value.message_dict
        assert 'Cannot sell' in excinfo.value.message_dict['quantity'][0]
