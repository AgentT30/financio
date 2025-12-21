import pytest
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from transfers.models import Transfer
from accounts.models import BankAccount, BankAccountBalance
from creditcards.models import CreditCard, CreditCardBalance

@pytest.mark.django_db
class TestTransferViews:
    def test_transfer_list_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('transfers:transfer_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_transfer_create_view(self, client, test_user, bank_account, credit_card):
        client.force_login(test_user)
        url = reverse('transfers:transfer_create')
        form_data = {
            'amount': '200.00',
            'method_type': 'upi',
            'memo': 'Bank to Card',
            'from_account': f"{bank_account.id}|bankaccount",
            'to_account': f"{credit_card.id}|creditcard",
            'date': timezone.now().date().isoformat()
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        
        # Verify transfer created
        assert Transfer.objects.filter(memo='Bank to Card').exists()
        transfer = Transfer.objects.get(memo='Bank to Card')
        
        # Verify balances updated
        bank_account.refresh_from_db()
        credit_card.refresh_from_db()
        
        # Bank: 1000 - 200 = 800
        assert bank_account.get_current_balance() == Decimal('800.00')
        # Card: 0 - 200 = -200 (Credit card balance semantics: negative = debt)
        # Wait, LedgerService.create_transfer_entry:
        # from_account: delta = -amount
        # to_account: delta = +amount
        # For Bank -> Card:
        # Bank balance += -200 (800)
        # Card balance += +200 (200)
        # In creditcards/models.py: "Negative balance = Amount owed"
        # So if I transfer 200 FROM Bank TO Card, I am paying 200 to the card.
        # This should INCREASE the card balance (make it less negative or more positive).
        # Let's check LedgerService again.
        assert credit_card.get_current_balance() == Decimal('200.00')

    def test_transfer_delete_view(self, client, test_user, bank_account, credit_card):
        client.force_login(test_user)
        
        # Create transfer
        create_url = reverse('transfers:transfer_create')
        client.post(create_url, {
            'amount': '100.00',
            'method_type': 'upi',
            'memo': 'Delete Me',
            'from_account': f"{bank_account.id}|bankaccount",
            'to_account': f"{credit_card.id}|creditcard",
            'date': timezone.now().date().isoformat()
        })
        
        transfer = Transfer.objects.get(memo='Delete Me')
        bank_account.refresh_from_db()
        credit_card.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('900.00')
        assert credit_card.get_current_balance() == Decimal('100.00')
        
        # Delete
        delete_url = reverse('transfers:transfer_delete', kwargs={'pk': transfer.pk})
        response = client.post(delete_url)
        assert response.status_code == 302
        
        # Verify soft delete
        transfer.refresh_from_db()
        assert transfer.is_deleted()
        
        # Verify balances reversed
        bank_account.refresh_from_db()
        credit_card.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('1000.00')
        assert credit_card.get_current_balance() == Decimal('0.00')
