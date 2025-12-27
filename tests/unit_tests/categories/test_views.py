import pytest
from django.urls import reverse
from categories.models import Category
from transactions.models import Transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from decimal import Decimal

@pytest.mark.django_db
class TestCategoryViews:
    def test_category_list_view(self, client, test_user):
        client.force_login(test_user)
        Category.objects.create(user=test_user, name='Shopping', type='expense')
        url = reverse('category_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Shopping' in response.content.decode()

    def test_category_create_view(self, client, test_user):
        client.force_login(test_user)
        url = reverse('category_create')
        form_data = {
            'name': 'New Category',
            'type': 'expense',
            'color': '#00FF00'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        assert Category.objects.filter(user=test_user, name='new category').exists()

    def test_category_edit_view(self, client, test_user):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Old Name', type='expense')
        url = reverse('category_edit', kwargs={'pk': category.pk})
        form_data = {
            'name': 'Updated Name',
            'type': 'expense',
            'color': '#0000FF'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302
        category.refresh_from_db()
        assert category.name == 'updated name'

    def test_category_delete_view_success(self, client, test_user):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='Delete Me', type='expense')
        url = reverse('category_delete', kwargs={'pk': category.pk})
        
        # GET confirmation
        response = client.get(url)
        assert response.status_code == 200
        
        # POST delete
        response = client.post(url)
        assert response.status_code == 302
        assert not Category.objects.filter(pk=category.pk).exists()

    def test_category_delete_view_failure_with_transactions(self, client, test_user, bank_account):
        client.force_login(test_user)
        category = Category.objects.create(user=test_user, name='In Use', type='expense')
        
        # Add transaction
        ct = ContentType.objects.get_for_model(bank_account.__class__)
        Transaction.objects.create(
            user=test_user,
            category=category,
            amount=Decimal('10.00'),
            transaction_type='expense',
            datetime_ist=timezone.now(),
            method_type='cash',
            purpose='test',
            account_content_type=ct,
            account_object_id=bank_account.id
        )
        
        url = reverse('category_delete', kwargs={'pk': category.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert Category.objects.filter(pk=category.pk).exists()
        # Should show error message
        follow_response = client.get(response.url)
        assert 'Cannot delete' in follow_response.content.decode()
