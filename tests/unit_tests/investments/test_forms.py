import pytest
from decimal import Decimal
from datetime import date
from investments.forms import BrokerForm, InvestmentForm, InvestmentTransactionForm, InvestmentCreationForm
from investments.models import Broker, Investment

@pytest.mark.django_db
class TestInvestmentForms:
    def test_broker_form_valid(self, test_user):
        form_data = {
            'name': 'Zerodha',
            'broker_user_id': 'AB1234',
            'demat_account_number': '1234567890123456'
        }
        form = BrokerForm(data=form_data)
        assert form.is_valid()
        broker = form.save(commit=False)
        broker.user = test_user
        broker.save()
        assert broker.name == 'Zerodha'

    def test_investment_form_broker_filtering(self, test_user, other_user):
        user_broker = Broker.objects.create(user=test_user, name='User Broker')
        other_broker = Broker.objects.create(user=other_user, name='Other Broker')
        
        form = InvestmentForm(user=test_user)
        assert user_broker in form.fields['broker'].queryset
        assert other_broker not in form.fields['broker'].queryset

    def test_investment_transaction_form_validation(self, test_user):
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        inv = Investment.objects.create(user=test_user, broker=broker, name='TCS', current_price=Decimal('3000'))
        
        # Negative price
        form_data = {
            'transaction_type': 'buy',
            'date': date.today(),
            'quantity': 10,
            'price_per_unit': -100,
            'fees': 0
        }
        form = InvestmentTransactionForm(data=form_data)
        assert not form.is_valid()
        assert 'price_per_unit' in form.errors

    def test_investment_creation_form_success(self, test_user):
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        form_data = {
            'name': 'Reliance',
            'symbol': 'RELIANCE',
            'broker': broker.id,
            'investment_type': 'stock',
            'transaction_type': 'buy',
            'current_price': '2500.00',
            'quantity': '10',
            'fees': '50.00',
            'purchase_date': date.today().isoformat(),
            'notes': 'Initial buy'
        }
        form = InvestmentCreationForm(user=test_user, data=form_data)
        assert form.is_valid()
        investment = form.save()
        assert investment.name == 'Reliance'
        assert investment.transactions.count() == 1
        assert investment.total_quantity == Decimal('10.00')
