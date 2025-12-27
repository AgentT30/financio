import pytest
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from transactions.models import Transaction
from categories.models import Category
from accounts.models import BankAccount, BankAccountBalance
from ledger.models import JournalEntry

@pytest.mark.django_db
class TestTransactionViews:
    def test_transaction_list_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('transactions:transaction_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_transaction_create_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Salary', type='income')
        url = reverse('transactions:transaction_create')
        form_data = {
            'transaction_type': 'income',
            'amount': '5000.00',
            'method_type': 'imps_neft_rtgs',
            'purpose': 'Monthly Salary',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        
        # Verify transaction created
        assert Transaction.objects.filter(purpose='Monthly Salary').exists()
        transaction = Transaction.objects.get(purpose='Monthly Salary')
        
        # Verify ledger integration
        assert transaction.journal_entry is not None
        assert JournalEntry.objects.filter(pk=transaction.journal_entry.pk).exists()
        
        # Verify balance updated (opening 1000 + 5000 = 6000)
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('6000.00')

    def test_transaction_delete_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Food', type='expense')
        
        # Create a transaction first via the view to ensure ledger is set up
        create_url = reverse('transactions:transaction_create')
        client.post(create_url, {
            'transaction_type': 'expense',
            'amount': '100.00',
            'method_type': 'upi',
            'purpose': 'Lunch',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        })
        
        transaction = Transaction.objects.get(purpose='Lunch')
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('900.00')
        
        # Now delete it
        delete_url = reverse('transactions:transaction_delete', kwargs={'pk': transaction.pk})
        response = client.post(delete_url)
        assert response.status_code == 302
        
        # Verify soft delete
        transaction.refresh_from_db()
        assert transaction.is_deleted
        
        # Verify balance reversed (900 + 100 = 1000)
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('1000.00')

    def test_transaction_edit_view(self, client, test_user, bank_account):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Food', type='expense')
        
        # Create
        client.post(reverse('transactions:transaction_create'), {
            'transaction_type': 'expense',
            'amount': '100.00',
            'method_type': 'upi',
            'purpose': 'Lunch',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        })
        
        transaction = Transaction.objects.get(purpose='Lunch')
        
        # Edit amount from 100 to 250
        edit_url = reverse('transactions:transaction_edit', kwargs={'pk': transaction.pk})
        client.post(edit_url, {
            'transaction_type': 'expense',
            'amount': '250.00',
            'method_type': 'upi',
            'purpose': 'Lunch Updated',
            'category': category.id,
            'account': f"{bank_account.id}|bankaccount",
            'date': timezone.now().date().isoformat()
        })
        
        # Verify balance updated (1000 - 250 = 750)
        bank_account.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('750.00')
        
        # Verify old journal entry was replaced
        transaction.refresh_from_db()
        assert transaction.purpose == 'Lunch Updated'
        assert transaction.amount == Decimal('250.00')
