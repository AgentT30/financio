from django import forms
from django.core.exceptions import ValidationError
from .models import Category


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'parent', 'type', 'color', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Category name'
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-14 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full h-14 px-4 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Icon name or emoji (optional)'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-lg bg-white dark:bg-dark-surface border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                'placeholder': 'Description (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter parent choices to only show user's categories
        if self.user:
            # Exclude the current instance from parent choices to prevent self-reference
            queryset = Category.objects.filter(user=self.user)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            self.fields['parent'].queryset = queryset
        
        # Make parent optional
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = "None (Top Level)"
    
    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        
        # Check depth limit (max 3 levels)
        if parent:
            depth = 1
            current = parent
            while current.parent:
                depth += 1
                current = current.parent
                if depth >= 3:
                    raise ValidationError('Maximum category depth is 3 levels.')
        
        return cleaned_data
