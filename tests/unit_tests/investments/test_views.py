import pytest
from django.urls import reverse
from decimal import Decimal
from datetime import date
from investments.models import Broker, Investment, InvestmentTransaction

@pytest.mark.django_db
class TestInvestmentViews:
    def test_broker_list_view(self, client, test_user):
        client.force_login(test_user)
        Broker.objects.create(user=test_user, name='Zerodha')
        url = reverse('investments:broker_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Zerodha' in response.content.decode()

    def test_broker_create_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('investments:broker_create')
        form_data = {
            'name': 'Groww',
            'broker_user_id': 'G123',
            'demat_account_number': '9876543210987654'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert Broker.objects.filter(name='Groww', user=test_user).exists()

    def test_investment_list_view(self, client, test_user):
        client.force_login(test_user)
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        Investment.objects.create(user=test_user, broker=broker, name='TCS', current_price=Decimal('3000'))
        url = reverse('investments:investment_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'TCS' in response.content.decode()

    def test_investment_create_smart_form(self, client, test_user):
        client.force_login(test_user)
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        url = reverse('investments:investment_create')
        form_data = {
            'name': 'Infosys',
            'symbol': 'INFY',
            'broker': broker.id,
            'investment_type': 'stock',
            'transaction_type': 'buy',
            'current_price': '1500.00',
            'quantity': '20',
            'purchase_date': date.today().isoformat()
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert Investment.objects.filter(name='Infosys').exists()
        inv = Investment.objects.get(name='Infosys')
        assert inv.transactions.count() == 1

    def test_transaction_delete_auto_removes_investment(self, client, test_user):
        client.force_login(test_user)
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        inv = Investment.objects.create(user=test_user, broker=broker, name='To Be Deleted', current_price=Decimal('100'))
        txn = InvestmentTransaction.objects.create(
            investment=inv,
            transaction_type='buy',
            quantity=Decimal('10'),
            price_per_unit=Decimal('100'),
            total_amount=Decimal('1000')
        )
        
        url = reverse('investments:transaction_delete', kwargs={'pk': txn.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not InvestmentTransaction.objects.filter(pk=txn.pk).exists()
        assert not Investment.objects.filter(pk=inv.pk).exists()

    def test_broker_archive_with_active_investments_fails(self, client, test_user):
        client.force_login(test_user)
        broker = Broker.objects.create(user=test_user, name='Zerodha')
        Investment.objects.create(user=test_user, broker=broker, name='Active Stock', status='active')
        
        url = reverse('investments:broker_archive', kwargs={'pk': broker.pk})
        response = client.post(url)
        assert response.status_code == 302 # Redirects with error message
        broker.refresh_from_db()
        assert broker.status == 'active'
