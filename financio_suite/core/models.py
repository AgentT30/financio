from django.db import models

"""
Core models - Base classes for all account types
"""
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class BaseAccount(models.Model):
    """
    Abstract base model for all account types.
    Provides common fields shared across all financial accounts.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        help_text="Account owner"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name/nickname for the account"
    )
    
    # Financial Information
    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        help_text="Initial balance when account was opened"
    )
    currency = models.CharField(
        max_length=3,
        default='INR',
        help_text="Currency code (fixed to INR for V1)"
    )
    
    # Dates and Status
    opened_on = models.DateField(
        null=True,
        blank=True,
        help_text="Date when account was opened"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Account status"
    )
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about the account"
    )
    
    # Visual Customization
    picture = models.ImageField(
        upload_to='account_pictures/',
        null=True,
        blank=True,
        help_text="Account picture/icon (optional)"
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Color theme for account (hex code, e.g., #3B82F6)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when account was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def clean(self):
        """Validate common fields"""
        # Validate currency is INR for V1
        if self.currency != 'INR':
            raise ValidationError({
                'currency': 'Only INR currency is supported in V1'
            })
        
        # Validate color format if provided
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError({
                'color': 'Color must be a valid hex code (e.g., #3B82F6)'
            })
    
    def archive(self):
        """Archive the account (soft delete)"""
        self.status = 'archived'
        self.save(update_fields=['status', 'updated_at'])
    
    def activate(self):
        """Activate an archived account"""
        self.status = 'active'
        self.save(update_fields=['status', 'updated_at'])
    
    def get_current_balance(self):
        """
        Get current balance - to be implemented by subclasses.
        Each account type will have its own balance relationship.
        """
        raise NotImplementedError("Subclasses must implement get_current_balance()")

