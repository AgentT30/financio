import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from accounts.models import BankAccount, DebitCard, BankAccountBalance
from transactions.models import Transaction
from categories.models import Category

@pytest.mark.django_db
class TestDebitCard:
    @pytest.fixture
    def setup_data(self, test_user):
        bank = BankAccount.objects.create(
            user=test_user,
            name='Test Bank',
            opening_balance=Decimal('1000.00'),
            currency='INR'
        )
        BankAccountBalance.objects.create(
            account=bank,
            balance_amount=Decimal('1000.00')
        )
        category = Category.objects.create(
            user=test_user,
            name='Food',
            type='expense'
        )
        return bank, category

    def test_debit_card_creation_and_encryption(self, test_user, setup_data):
        bank, _ = setup_data
        card = DebitCard.objects.create(
            user=test_user,
            bank_account=bank,
            name='Test Debit Card',
            card_number='1234567890123456',
            cvv='123',
            expiry_date=date(2030, 12, 31)
        )
        assert card.card_number_last4 == '3456'
        assert card.get_masked_card_number() == '****3456'
        assert card.card_number == '1234567890123456'

    def test_debit_card_validation(self, test_user, setup_data):
        bank, _ = setup_data
        with pytest.raises(ValidationError):
            card = DebitCard(
                user=test_user,
                bank_account=bank,
                name='Invalid Card',
                card_number='abcd1234efgh',
                expiry_date=date(2030, 12, 31)
            )
            card.full_clean()

    def test_transaction_with_debit_card(self, test_user, setup_data):
        bank, category = setup_data
        card = DebitCard.objects.create(
            user=test_user,
            bank_account=bank,
            name='My Card',
            card_number='1234567812345678',
            expiry_date=date(2030, 1, 1)
        )
        
        transaction = Transaction.objects.create(
            user=test_user,
            datetime_ist=timezone.now(),
            transaction_type='expense',
            amount=Decimal('100.00'),
            account_content_type=ContentType.objects.get_for_model(bank),
            account_object_id=bank.id,
            debit_card=card,
            category=category,
            purpose='Pizza',
            method_type='card'
        )
        
        assert transaction.debit_card == card
        assert transaction.method_type == 'card'

    def test_bank_balance_inheritance(self, test_user, setup_data):
        bank, _ = setup_data
        card = DebitCard.objects.create(
            user=test_user,
            bank_account=bank,
            name='My Card',
            card_number='1234567812345678',
            expiry_date=date(2030, 1, 1)
        )
        assert card.get_current_balance() == Decimal('1000.00')
