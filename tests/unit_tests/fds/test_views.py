import pytest
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from fds.models import FixedDeposit

@pytest.mark.django_db
class TestFixedDepositViews:
    def test_fd_list_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('fds:fd_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_fd_create_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('fds:fd_create')
        form_data = {
            'name': 'New FD',
            'institution': 'SBI',
            'principal_amount': '50000.00',
            'interest_rate': '7.00',
            'maturity_amount': '65000.00',
            'tenure_months': '36',
            'opened_on': date.today().isoformat(),
            'maturity_date': (date.today() + timedelta(days=1095)).isoformat(),
            'status': 'active',
            'compounding_frequency': 'monthly'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert FixedDeposit.objects.filter(name='New FD').exists()

    def test_fd_edit_view(self, client, test_user):
        fd = FixedDeposit.objects.create(
            user=test_user,
            name='Old FD',
            institution='SBI',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('11000.00'),
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365),
            status='active'
        )
        client.force_login(test_user)
        url = reverse('fds:fd_edit', kwargs={'pk': fd.pk})
        form_data = {
            'name': 'Updated FD',
            'institution': 'SBI',
            'principal_amount': '10000.00',
            'interest_rate': '6.00',
            'maturity_amount': '11500.00',
            'tenure_months': '12',
            'opened_on': date.today().isoformat(),
            'maturity_date': (date.today() + timedelta(days=365)).isoformat(),
            'status': 'active',
            'compounding_frequency': 'quarterly'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        fd.refresh_from_db()
        assert fd.name == 'Updated FD'
        assert fd.interest_rate == Decimal('6.00')

    def test_fd_delete_view(self, client, test_user):
        fd = FixedDeposit.objects.create(
            user=test_user,
            name='Delete FD',
            institution='SBI',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('11000.00'),
            tenure_months=12,
            opened_on=date.today(),
            maturity_date=date.today() + timedelta(days=365),
            status='active'
        )
        client.force_login(test_user)
        url = reverse('fds:fd_delete', kwargs={'pk': fd.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not FixedDeposit.objects.filter(pk=fd.pk).exists()

    def test_fd_mark_matured_view(self, client, test_user):
        fd = FixedDeposit.objects.create(
            user=test_user,
            name='Matured FD',
            institution='SBI',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            maturity_amount=Decimal('11000.00'),
            tenure_months=12,
            opened_on=date.today() - timedelta(days=400),
            maturity_date=date.today() - timedelta(days=35),
            status='active'
        )
        client.force_login(test_user)
        url = reverse('fds:fd_mark_matured', kwargs={'pk': fd.pk})
        response = client.post(url)
        assert response.status_code == 302
        fd.refresh_from_db()
        assert fd.status == 'archived'
