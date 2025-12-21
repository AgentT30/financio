import pytest
from django.urls import reverse
from accounts.models import BankAccount, BankAccountBalance
from decimal import Decimal

@pytest.mark.django_db
class TestAccountViews:
    def test_account_list_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        url = reverse('account_list')
        response = client.get(url)
        assert response.status_code == 200
        assert bank_account.name in response.content.decode()

    def test_account_create_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('account_create')
        form_data = {
            'name': 'New Account',
            'account_type': 'savings',
            'institution': 'New Bank',
            'opening_balance': '2000.00',
            'status': 'active'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert BankAccount.objects.filter(name='New Account').exists()
        account = BankAccount.objects.get(name='New Account')
        assert BankAccountBalance.objects.filter(account=account).exists()

    def test_account_edit_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        url = reverse('account_edit', kwargs={'pk': bank_account.pk})
        form_data = {
            'name': 'Updated Name',
            'account_type': 'savings',
            'institution': 'Test Bank',
            'opening_balance': '1500.00', # Changed from 1000.00
            'status': 'active'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        bank_account.refresh_from_db()
        assert bank_account.name == 'Updated Name'
        assert bank_account.balance.balance_amount == Decimal('1500.00')

    def test_account_detail_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        url = reverse('account_detail', kwargs={'pk': bank_account.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert bank_account.name in response.content.decode()

    def test_account_delete_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        url = reverse('account_delete', kwargs={'pk': bank_account.pk})
        # GET confirmation page
        response = client.get(url)
        assert response.status_code == 200
        
        # POST delete
        response = client.post(url)
        assert response.status_code == 302
        assert not BankAccount.objects.filter(pk=bank_account.pk).exists()

    def test_account_toggle_status_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        url = reverse('account_toggle_status', kwargs={'pk': bank_account.pk})
        
        # Toggle to archived
        response = client.post(url)
        assert response.status_code == 302
        bank_account.refresh_from_db()
        assert bank_account.status == 'archived'
        
        # Toggle back to active
        response = client.post(url)
        assert response.status_code == 302
        bank_account.refresh_from_db()
        assert bank_account.status == 'active'
