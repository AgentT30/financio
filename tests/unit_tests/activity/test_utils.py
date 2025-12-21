import pytest
from django.http import HttpRequest
from activity.utils import log_activity, track_model_changes
from activity.models import ActivityLog
from accounts.models import BankAccount
from decimal import Decimal

@pytest.mark.django_db
class TestActivityUtils:
    def test_log_activity_with_request(self, test_user):
        account = BankAccount.objects.create(user=test_user, name='Test Bank')
        
        # Mock request
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestAgent'
        
        log = log_activity(
            user=test_user,
            action='create',
            obj=account,
            changes={'name': 'Test Bank'},
            request=request
        )
        
        assert isinstance(log, ActivityLog)
        assert log.user == test_user
        assert log.action == 'create'
        assert log.object_id == account.id
        assert log.ip_address == '127.0.0.1'
        assert log.user_agent == 'TestAgent'
        assert log.changes == {'name': 'Test Bank'}

    def test_log_activity_without_request(self, test_user):
        account = BankAccount.objects.create(user=test_user, name='Test Bank')
        
        log = log_activity(
            user=test_user,
            action='delete',
            obj=account
        )
        
        assert log.ip_address is None
        assert log.user_agent is None

    def test_track_model_changes(self, test_user):
        old_account = BankAccount(name='Old Name', opening_balance=Decimal('100.00'))
        new_account = BankAccount(name='New Name', opening_balance=Decimal('200.00'))
        
        fields = ['name', 'opening_balance', 'status']
        changes = track_model_changes(old_account, new_account, fields)
        
        assert 'name' in changes
        assert changes['name']['before'] == 'Old Name'
        assert changes['name']['after'] == 'New Name'
        
        assert 'opening_balance' in changes
        assert changes['opening_balance']['before'] == '100.00'
        assert changes['opening_balance']['after'] == '200.00'
        
        # status didn't change (both None or same default)
        assert 'status' not in changes

    def test_track_model_changes_no_diff(self, test_user):
        account = BankAccount(name='Same')
        changes = track_model_changes(account, account, ['name'])
        assert changes is None
