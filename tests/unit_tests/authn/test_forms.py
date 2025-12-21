import pytest
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from authn.forms import SignupForm, RecoveryPasswordResetForm
from authn.models import UserRecovery

@pytest.mark.django_db
class TestSignupForm:
    def test_signup_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'FinancioTest@2025',
            'password2': 'FinancioTest@2025'
        }
        form = SignupForm(data=form_data)
        assert form.is_valid()
        user = form.save()
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'

    def test_signup_form_duplicate_email(self, test_user):
        test_user.email = 'test@example.com'
        test_user.save()
        
        form_data = {
            'username': 'anotheruser',
            'email': 'test@example.com',
            'password1': 'FinancioTest@2025',
            'password2': 'FinancioTest@2025'
        }
        form = SignupForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

@pytest.mark.django_db
class TestRecoveryPasswordResetForm:
    def test_reset_form_valid(self, test_user):
        token = 'recoverytoken123'
        UserRecovery.objects.create(
            user=test_user,
            token_hash=make_password(token)
        )
        
        form_data = {
            'username': test_user.username,
            'recovery_token': token,
            'new_password1': 'FinancioTest@2025',
            'new_password2': 'FinancioTest@2025'
        }
        form = RecoveryPasswordResetForm(data=form_data)
        assert form.is_valid()
        form.save()
        test_user.refresh_from_db()
        assert test_user.check_password('FinancioTest@2025')

    def test_reset_form_invalid_token(self, test_user):
        UserRecovery.objects.create(
            user=test_user,
            token_hash=make_password('correcttoken')
        )
        
        form_data = {
            'username': test_user.username,
            'recovery_token': 'wrongtoken',
            'new_password1': 'FinancioTest@2025',
            'new_password2': 'FinancioTest@2025'
        }
        form = RecoveryPasswordResetForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors # Non-field error for invalid token
