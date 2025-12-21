import pytest
from django.contrib.contenttypes.models import ContentType
from activity.models import ActivityLog
from accounts.models import BankAccount

@pytest.mark.django_db
class TestActivityLogModel:
    def test_activity_log_creation(self, test_user):
        # Create a dummy object to log activity for
        account = BankAccount.objects.create(
            user=test_user,
            name='Test Account',
            account_type='savings'
        )
        content_type = ContentType.objects.get_for_model(account)
        
        log = ActivityLog.objects.create(
            user=test_user,
            action='create',
            content_type=content_type,
            object_id=account.id,
            object_repr=str(account),
            changes={'name': {'before': None, 'after': 'Test Account'}}
        )
        
        assert log.user == test_user
        assert log.action == 'create'
        assert log.content_object == account
        assert log.object_repr == str(account)
        assert log.changes['name']['after'] == 'Test Account'
        assert str(log).startswith(test_user.username)

    def test_activity_log_generic_relation(self, test_user):
        account = BankAccount.objects.create(user=test_user, name='Bank')
        content_type = ContentType.objects.get_for_model(account)
        
        log = ActivityLog.objects.create(
            user=test_user,
            action='update',
            content_type=content_type,
            object_id=account.id,
            object_repr='Bank'
        )
        
        assert log.content_object == account
