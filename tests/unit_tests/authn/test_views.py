import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from authn.models import UserRecovery
from django.contrib.auth.hashers import make_password

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
