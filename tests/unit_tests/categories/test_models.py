import pytest
from django.core.exceptions import ValidationError
from categories.models import Category
from transactions.models import Transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from decimal import Decimal

@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation_and_normalization(self, test_user):
        category = Category.objects.create(
            user=test_user,
            name='Groceries',
            type='expense'
        )
        assert category.name == 'groceries'  # Normalization to lowercase
        assert str(category) == 'Expense: groceries'

    def test_hierarchy_depth_limit(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Level 1', type='expense')
        cat2 = Category.objects.create(user=test_user, name='Level 2', type='expense', parent=cat1)
        cat3 = Category.objects.create(user=test_user, name='Level 3', type='expense', parent=cat2)
        
        # Level 4 should fail
        cat4 = Category(user=test_user, name='Level 4', type='expense', parent=cat3)
        with pytest.raises(ValidationError) as excinfo:
            cat4.clean()
        assert "hierarchy cannot exceed 3 levels" in str(excinfo.value)

    def test_circular_reference_prevention(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Cat 1', type='expense')
        cat2 = Category.objects.create(user=test_user, name='Cat 2', type='expense', parent=cat1)
        
        # Try to make cat1 a child of cat2
        cat1.parent = cat2
        with pytest.raises(ValidationError) as excinfo:
            cat1.clean()
        assert "cannot be its own ancestor" in str(excinfo.value)

    def test_parent_child_type_match(self, test_user):
        income_cat = Category.objects.create(user=test_user, name='Income', type='income')
        expense_cat = Category(user=test_user, name='Expense', type='expense', parent=income_cat)
        
        with pytest.raises(ValidationError) as excinfo:
            expense_cat.clean()
        assert "must match child type" in str(excinfo.value)

    def test_color_validation(self, test_user):
        category = Category(user=test_user, name='Test', type='expense', color='blue')
        with pytest.raises(ValidationError) as excinfo:
            category.clean()
        assert "must be a hex code" in str(excinfo.value)
        
        category.color = '#3B82F6'
        category.clean() # Should pass

    def test_get_full_path(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Shopping', type='expense')
        cat2 = Category.objects.create(user=test_user, name='Groceries', type='expense', parent=cat1)
        assert cat2.get_full_path() == 'shopping > groceries'

    def test_can_delete_logic(self, test_user, bank_account):
        category = Category.objects.create(user=test_user, name='Test', type='expense')
        assert category.can_delete() is True
        
        # Test with subcategory
        child = Category.objects.create(user=test_user, name='Child', type='expense', parent=category)
        assert category.can_delete() is False
        child.delete()
        assert category.can_delete() is True
        
        # Test with transaction
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
        assert category.can_delete() is False
