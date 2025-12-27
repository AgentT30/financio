import pytest
from datetime import date, timedelta
from decimal import Decimal
from creditcards.forms import CreditCardForm
from creditcards.models import CreditCard

@pytest.mark.django_db
class TestCreditCardForm:
    def test_form_valid_data(self, test_user):
        form_data = {
            'name': 'HDFC Regalia',
            'institution': 'HDFC Bank',
            'card_number': '1234567890123456',
            'cvv': '123',
            'card_type': 'visa',
            'credit_limit': Decimal('100000.00'),
            'billing_day': 1,
            'due_day': 20,
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'opening_balance': Decimal('0.00'),
            'opened_on': date.today().isoformat(),
            'status': 'active'
        }
        form = CreditCardForm(data=form_data, user=test_user)
        assert form.is_valid()
        card = form.save()
        assert card.user == test_user
        assert card.card_number_last4 == '3456'

    def test_billing_due_day_same_validation(self, test_user):
        form_data = {
            'name': 'Test Card',
            'institution': 'Bank',
            'card_number': '1234567890123456',
            'cvv': '123',
            'billing_day': 15,
            'due_day': 15, # Same as billing day
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'credit_limit': Decimal('1000.00')
        }
        form = CreditCardForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'Billing day and due day should be different' in form.errors['__all__'][0]

    def test_cvv_optional_on_edit(self, test_user, credit_card):
        form_data = {
            'name': 'Updated Name',
            'institution': credit_card.institution,
            'card_number': '1234567890123456',
            'cvv': '', # Empty CVV on edit
            'card_type': 'visa',
            'credit_limit': credit_card.credit_limit,
            'billing_day': credit_card.billing_day,
            'due_day': credit_card.due_day,
            'expiry_date': credit_card.expiry_date.isoformat(),
            'opening_balance': credit_card.opening_balance,
            'status': 'active'
        }
        form = CreditCardForm(data=form_data, instance=credit_card, user=test_user)
        assert form.is_valid()
        card = form.save()
        assert card.cvv == '123' # Should preserve old CVV from fixture
