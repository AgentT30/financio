import pytest
from django.contrib.auth.models import User
from authn.models import UserRecovery

@pytest.mark.django_db
class TestUserRecoveryModel:
    def test_recovery_creation(self, test_user):
        recovery = UserRecovery.objects.create(
            user=test_user,
            token_hash='hashed_token'
        )
        assert recovery.user == test_user
        assert recovery.token_hash == 'hashed_token'
        assert str(recovery) == f"Recovery token for {test_user.username}"
