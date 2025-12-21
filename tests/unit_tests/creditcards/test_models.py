import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from creditcards.models import CreditCard, CreditCardBalance
from transactions.models import Transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

@pytest.mark.django_db
class TestCreditCardModel:
    def test_credit_card_creation_and_masking(self, test_user):
        card = CreditCard.objects.create(
            user=test_user,
            name='My Card',
            institution='HDFC Bank',
            card_number='1234567890123456',
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('50000.00'),
            opening_balance=Decimal('0.00'),
            status='active'
        )
        assert card.card_number_last4 == '3456'
        assert card.get_masked_card_number() == '****3456'
        assert card.get_masked_cvv() == '***'
        assert str(card) == 'My Card (Visa ****3456)'

    def test_card_number_validation(self, test_user):
        card = CreditCard(
            user=test_user,
            name='Invalid Card',
            institution='Bank',
            card_number='1234abcd', # Not digits
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('1000.00')
        )
        with pytest.raises(ValidationError) as excinfo:
            card.full_clean()
        assert 'card_number' in excinfo.value.message_dict

    def test_cvv_validation(self, test_user):
        card = CreditCard(
            user=test_user,
            name='Invalid CVV',
            institution='Bank',
            card_number='1234567890123',
            cvv='abc', # Not digits
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('1000.00')
        )
        with pytest.raises(ValidationError) as excinfo:
            card.full_clean()
        assert 'cvv' in excinfo.value.message_dict

    def test_expiry_date_validation(self, test_user):
        card = CreditCard(
            user=test_user,
            name='Expired Card',
            institution='Bank',
            card_number='1234567890123',
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() - timedelta(days=1), # Past date
            credit_limit=Decimal('1000.00')
        )
        with pytest.raises(ValidationError) as excinfo:
            card.full_clean()
        assert 'expiry_date' in excinfo.value.message_dict

    def test_available_credit_calculation(self, test_user):
        card = CreditCard.objects.create(
            user=test_user,
            name='Credit Test',
            institution='Bank',
            card_number='1234567890123',
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('50000.00'),
            opening_balance=Decimal('0.00')
        )
        CreditCardBalance.objects.create(account=card, balance_amount=Decimal('-5000.00'))
        
        # Available = 50000 + (-5000) = 45000
        assert card.available_credit() == Decimal('45000.00')
        assert card.amount_owed() == Decimal('5000.00')

    def test_can_delete_logic(self, test_user):
        card = CreditCard.objects.create(
            user=test_user,
            name='Delete Test',
            institution='Bank',
            card_number='1234567890123',
            cvv='123',
            billing_day=1,
            due_day=20,
            expiry_date=date.today() + timedelta(days=365),
            credit_limit=Decimal('50000.00')
        )
        assert card.can_delete() is True
        
        # Add transaction
        ct = ContentType.objects.get_for_model(CreditCard)
        Transaction.objects.create(
            user=test_user,
            amount=Decimal('100.00'),
            transaction_type='expense',
            datetime_ist=timezone.now(),
            method_type='card',
            purpose='test',
            account_content_type=ct,
            account_object_id=card.id
        )
        assert card.can_delete() is False
