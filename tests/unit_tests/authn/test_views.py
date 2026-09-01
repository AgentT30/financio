import pytest
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from authn.models import UserRecovery
from django.contrib.auth.hashers import make_password
from accounts.models import BankAccount, BankAccountBalance, DebitCard
from creditcards.models import CreditCard
from categories.models import Category
from transactions.models import Transaction
from transfers.models import Transfer
from ledger.models import JournalEntry, Posting
from activity.models import ActivityLog
from fds.models import FixedDeposit
from investments.models import Broker, Investment

@pytest.mark.django_db
class TestAuthViews:
    def test_login_view_get(self, client):
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'auth/login.html' in [t.name for t in response.templates]

    def test_login_view_post(self, client, test_user):
        url = reverse('login')
        response = client.post(url, {
            'username': test_user.username,
            'password': 'FinancioTest@2025'
        })
        assert response.status_code == 302
        assert response.url == reverse('dashboard')

    def test_signup_view_post(self, client):
        url = reverse('signup')
        response = client.post(url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'FinancioTest@2025',
            'password2': 'FinancioTest@2025'
        })
        assert response.status_code == 302
        assert response.url == reverse('signup_success')
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')
        assert UserRecovery.objects.filter(user=user).exists()

    def test_logout_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('logout')
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('login')

    def test_password_reset_request_view(self, client, test_user):
        token = 'recoverytoken123'
        UserRecovery.objects.create(
            user=test_user,
            token_hash=make_password(token)
        )
        url = reverse('password_reset')
        response = client.post(url, {
            'username': test_user.username,
            'recovery_token': token,
            'new_password1': 'FinancioTest@2025',
            'new_password2': 'FinancioTest@2025'
        })
        assert response.status_code == 302
        assert response.url == reverse('login')
        test_user.refresh_from_db()
        assert test_user.check_password('FinancioTest@2025')

    def test_settings_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('settings')
        response = client.get(url)
        assert response.status_code == 200

    def test_account_delete_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('account_delete')
        # Incorrect confirmation text
        response = client.post(url, {'confirmation_text': 'Wrong'})
        assert response.status_code == 302
        assert User.objects.filter(pk=test_user.pk).exists()
        
        # Correct confirmation text
        response = client.post(url, {'confirmation_text': 'Yes I want to delete my account'})
        assert response.status_code == 302
        assert not User.objects.filter(pk=test_user.pk).exists()

    def test_reset_user_data_hard_deletes_financial_history_and_resets_balances(self, client, test_user, bank_account, credit_card):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Food', type='expense')
        bank_type = ContentType.objects.get_for_model(bank_account)
        card_type = ContentType.objects.get_for_model(credit_card)
        journal = JournalEntry.objects.create(user=test_user, occurred_at=date.today(), memo='History')
        Posting.objects.create(journal_entry=journal, account_content_type=bank_type, account_object_id=bank_account.id, amount=Decimal('100.00'), posting_type='debit')
        Transaction.objects.create(
            user=test_user, datetime_ist=date.today(), transaction_type='expense', amount='100.00',
            account_content_type=bank_type, account_object_id=bank_account.id, method_type='upi',
            purpose='History', category=category, journal_entry=journal,
        )
        Transfer.objects.create(
            user=test_user, datetime_ist=date.today(), amount='100.00',
            from_account_content_type=bank_type, from_account_object_id=bank_account.id,
            to_account_content_type=card_type, to_account_object_id=credit_card.id,
            method_type='upi', memo='History',
        )
        BankAccountBalance.objects.filter(account=bank_account).update(balance_amount=Decimal('800.00'))
        ActivityLog.objects.create(user=test_user, action='create', content_type=bank_type, object_id=bank_account.id, object_repr='History')

        response = client.post(reverse('reset_user_data'), {
            'action': 'reset', 'confirmation_text': 'Delete/Reset my account',
        })

        assert response.status_code == 302
        assert User.objects.filter(pk=test_user.pk).exists()
        assert not Transaction.objects.filter(user=test_user).exists()
        assert not Transfer.objects.filter(user=test_user).exists()
        assert not JournalEntry.objects.filter(user=test_user).exists()
        assert not Posting.objects.exists()
        assert not ActivityLog.objects.filter(user=test_user).exists()
        bank_account.refresh_from_db()
        credit_card.refresh_from_db()
        assert bank_account.get_current_balance() == Decimal('1000.00')
        assert credit_card.get_current_balance() == Decimal('0.00')

    def test_delete_all_user_data_keeps_user_and_recovery_record(self, client, test_user, bank_account, credit_card):
        client.force_login(test_user)
        recovery = UserRecovery.objects.create(user=test_user, token_hash=make_password('recovery-token'))
        category = Category.objects.create(user=test_user, name='Food', type='expense')
        broker = Broker.objects.create(user=test_user, name='Broker')
        Investment.objects.create(user=test_user, broker=broker, name='Fund', investment_type='mutual_fund', current_price='100.00')
        FixedDeposit.objects.create(
            user=test_user, name='FD', institution='Bank', principal_amount='1000.00', interest_rate='6.00',
            maturity_amount='1100.00', tenure_days=365, opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365),
        )
        DebitCard.objects.create(
            user=test_user, bank_account=bank_account, name='Debit', card_number='123456789012',
            expiry_date=date.today() + timedelta(days=365),
        )
        ActivityLog.objects.create(
            user=test_user, action='create', content_type=ContentType.objects.get_for_model(bank_account),
            object_id=bank_account.id, object_repr='Account',
        )

        response = client.post(reverse('reset_user_data'), {
            'action': 'delete', 'confirmation_text': 'Delete/Reset my account',
        })

        assert response.status_code == 302
        assert User.objects.filter(pk=test_user.pk).exists()
        assert UserRecovery.objects.filter(pk=recovery.pk).exists()
        assert not BankAccount.objects.filter(user=test_user).exists()
        assert not CreditCard.objects.filter(user=test_user).exists()
        assert not DebitCard.objects.filter(user=test_user).exists()
        assert not Category.objects.filter(user=test_user).exists()
        assert not Broker.objects.filter(user=test_user).exists()
        assert not Investment.objects.filter(user=test_user).exists()
        assert not FixedDeposit.objects.filter(user=test_user).exists()
        assert not ActivityLog.objects.filter(user=test_user).exists()
