from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from .models import Category
from .forms import CategoryForm


@login_required
def category_list(request):
    """Display all categories in a tree structure."""
    # Get top-level categories (no parent)
    categories = Category.objects.filter(
        user=request.user,
        parent__isnull=True
    ).prefetch_related('children', 'children__children').order_by('type', 'name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'categories/category_list.html', context)


@login_required
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Category',
        'button_text': 'Create Category',
    }
    return render(request, 'categories/category_form.html', context)


@login_required
def category_edit(request, pk):
    """Edit an existing category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Edit Category',
        'button_text': 'Update Category',
    }
    return render(request, 'categories/category_form.html', context)


@login_required
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = category.name.title()
        
        # Check if category can be deleted
        if not category.can_delete():
            # Check specific reasons for better error messages
            if category.children.filter(is_active=True).exists():
                messages.error(request, f'Cannot delete "{name}" because it has subcategories. Delete or reassign them first.')
            else:
                messages.error(request, f'Cannot delete "{name}" because it is being used by transactions.')
            return redirect('category_list')
        
        try:
            category.delete()
            messages.success(request, f'Category "{name}" deleted successfully!')
        except ProtectedError:
            # Catch ProtectedError if can_delete() check missed something
            messages.error(request, f'Cannot delete "{name}" because it is being used by transactions.')
        
        return redirect('category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'categories/category_confirm_delete.html', context)
