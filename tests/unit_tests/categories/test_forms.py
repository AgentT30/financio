import pytest
from categories.models import Category
from categories.forms import CategoryForm

@pytest.mark.django_db
class TestCategoryForm:
    def test_form_valid_data(self, test_user):
        form_data = {
            'name': 'Groceries',
            'type': 'expense',
            'color': '#FF0000',
            'icon': '🛒'
        }
        form = CategoryForm(data=form_data, user=test_user)
        assert form.is_valid()
        category = form.save(commit=False)
        category.user = test_user
        category.save()
        assert category.name == 'groceries'

    def test_parent_filtering(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Cat 1', type='expense')
        other_user_cat = Category.objects.create(
            user=pytest.importorskip("django.contrib.auth.models").User.objects.create_user(username='other', password='password'),
            name='Other',
            type='expense'
        )
        
        form = CategoryForm(user=test_user)
        assert cat1 in form.fields['parent'].queryset
        assert other_user_cat not in form.fields['parent'].queryset

    def test_exclude_self_from_parent(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Cat 1', type='expense')
        form = CategoryForm(instance=cat1, user=test_user)
        assert cat1 not in form.fields['parent'].queryset

    def test_form_depth_limit(self, test_user):
        cat1 = Category.objects.create(user=test_user, name='Level 1', type='expense')
        cat2 = Category.objects.create(user=test_user, name='Level 2', type='expense', parent=cat1)
        cat3 = Category.objects.create(user=test_user, name='Level 3', type='expense', parent=cat2)
        
        form_data = {
            'name': 'Level 4',
            'type': 'expense',
            'parent': cat3.id
        }
        form = CategoryForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'Maximum category depth is 3 levels.' in form.errors['__all__']
