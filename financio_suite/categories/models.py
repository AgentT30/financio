from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Category model for classifying transactions.
    Supports hierarchical structure (parent-child) with max 3 levels.
    System default categories owned by admin user.
    """
    
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('fee', 'Fee'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        db_index=True,
        help_text="Owner of the category (admin for defaults)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., Groceries, Salary)"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        help_text="Parent category for hierarchical structure"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        db_index=True,
        help_text="Category type: income, expense, transfer, or fee"
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Hex color code for UI visualization (e.g., #3B82F6)"
    )
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Icon name or emoji for category (e.g., 🍔, 🚗, 💰)"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description for the category"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="System default category (owned by admin)"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Active status (for soft delete/archive)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when category was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when category was last updated"
    )
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['type', 'name']
        unique_together = [['user', 'name', 'type']]
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_cat_user_active'),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"
    
    def clean(self):
        """Validate category constraints"""
        # Check hierarchy depth (max 3 levels)
        if self.parent:
            depth = self._get_depth()
            if depth > 3:
                raise ValidationError(
                    "Category hierarchy cannot exceed 3 levels (current depth would be {})".format(depth)
                )
        
        # Prevent circular references
        if self.parent:
            current = self.parent
            while current:
                if current.id == self.id:
                    raise ValidationError("Category cannot be its own ancestor")
                current = current.parent
        
        # Validate parent type matches child type
        if self.parent and self.parent.type != self.type:
            raise ValidationError(
                f"Parent category type ({self.parent.get_type_display()}) "
                f"must match child type ({self.get_type_display()})"
            )
        
        # Validate color format if provided
        if self.color and not self.color.startswith('#'):
            raise ValidationError("Color must be a hex code starting with #")
    
    def save(self, *args, **kwargs):
        """Override save to run validation and normalize data"""
        # Convert name to lowercase for consistent storage
        if self.name:
            self.name = self.name.lower()
        
        # Run validation
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _get_depth(self):
        """Calculate current depth in hierarchy"""
        depth = 1
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth
    
    def get_full_path(self):
        """Get hierarchical path (e.g., 'Expense > Shopping > Groceries')"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)
    
    def get_children(self):
        """Get all child categories"""
        return self.children.filter(is_active=True)
    
    def get_all_descendants(self):
        """Get all descendants recursively"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def can_delete(self):
        """Check if category can be deleted (not in use by transactions)"""
        # Will implement this check when Transaction model exists
        # For now, return True
        return True
    
    def get_depth(self):
        """Public method to get depth in hierarchy"""
        return self._get_depth()
