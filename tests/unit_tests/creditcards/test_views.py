import pytest
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from creditcards.models import CreditCard, CreditCardBalance

@pytest.mark.django_db
class TestCreditCardViews:
    def test_creditcard_list_view(self, client, test_user, credit_card):
        client.force_login(test_user)
        url = reverse('creditcard_list')
        response = client.get(url)
        assert response.status_code == 200
        assert credit_card.name in response.content.decode()

    def test_creditcard_create_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('creditcard_create')
        form_data = {
            'name': 'New Card',
            'institution': 'New Bank',
            'card_number': '1111222233334444',
            'cvv': '999',
            'card_type': 'mastercard',
            'credit_limit': '50000.00',
            'billing_day': '5',
            'due_day': '25',
            'expiry_date': (date.today() + timedelta(days=730)).isoformat(),
            'opening_balance': '0.00',
            'status': 'active'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert CreditCard.objects.filter(name='New Card').exists()
        card = CreditCard.objects.get(name='New Card')
        assert CreditCardBalance.objects.filter(account=card).exists()

    def test_creditcard_edit_view(self, client, test_user, credit_card):
        client.force_login(test_user)
        url = reverse('creditcard_edit', kwargs={'pk': credit_card.pk})
        form_data = {
            'name': 'Updated Card Name',
            'institution': credit_card.institution,
            'card_number': '1234567890123',
            'cvv': '123',
            'card_type': 'visa',
            'credit_limit': '60000.00',
            'billing_day': credit_card.billing_day,
            'due_day': credit_card.due_day,
            'expiry_date': credit_card.expiry_date.isoformat(),
            'opening_balance': '0.00',
            'status': 'active'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        credit_card.refresh_from_db()
        assert credit_card.name == 'Updated Card Name'
        assert credit_card.credit_limit == Decimal('60000.00')

    def test_creditcard_delete_view_success(self, client, test_user):
        client.force_login(test_user)
        card = CreditCard.objects.create(
            user=test_user,
            name='Delete Me',
            institution='Bank',
            card_number='1234567890123',
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('1000.00')
        )
        url = reverse('creditcard_delete', kwargs={'pk': card.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not CreditCard.objects.filter(pk=card.pk).exists()

    def test_creditcard_toggle_status_view(self, client, test_user, credit_card):
        client.force_login(test_user)
        url = reverse('creditcard_toggle_status', kwargs={'pk': credit_card.pk})
        
        # Archive
        response = client.get(url)
        assert response.status_code == 302
        credit_card.refresh_from_db()
        assert credit_card.status == 'archived'
        
        # Activate
        client.get(url)
        credit_card.refresh_from_db()
        assert credit_card.status == 'active'
