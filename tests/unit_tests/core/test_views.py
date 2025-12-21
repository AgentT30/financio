import pytest
from django.urls import reverse
from accounts.models import BankAccount
from decimal import Decimal

@pytest.mark.django_db
class TestCoreViews:
    def test_dashboard_view_anonymous(self, client):
        url = reverse('dashboard')
        response = client.get(url)
        assert response.status_code == 302 # Redirect to login

    def test_dashboard_view_authenticated(self, client, test_user):
        client.force_login(test_user)
        
        # Create some data to show on dashboard
        BankAccount.objects.create(
            user=test_user,
            name='Dashboard Bank',
            opening_balance=Decimal('5000.00'),
            status='active'
        )
        
        url = reverse('dashboard')
        response = client.get(url)
        assert response.status_code == 200
        # Net worth should be visible (formatted with Indian numbering)
        assert '5,000' in response.content.decode() 
        
        # Check stats in context
        assert 'stats' in response.context
        assert response.context['stats']['net_worth'] == Decimal('5000.00')
        assert response.context['stats']['total_banks'] == 1
