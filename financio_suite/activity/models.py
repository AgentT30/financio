from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ActivityLog(models.Model):
    """
    Audit log for tracking user actions (CRUD operations).
    Uses GenericForeignKey to reference any model.
    """
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('archive', 'Archive'),
        ('activate', 'Activate'),
    ]
    
    # User who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        db_index=True,
        help_text="User who performed the action"
    )
    
    # Action performed
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed"
    )
    
    # Object being acted upon (GenericForeignKey)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of object (Transaction, Account, etc.)"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the object"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Object representation (store string in case object is deleted)
    object_repr = models.CharField(
        max_length=200,
        help_text="String representation of object"
    )
    
    # Change details
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="Field-level changes (for updates) in JSON format"
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of user"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Browser user agent"
    )
    
    # Timestamp (IST via Django's TIME_ZONE setting)
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When action was performed (IST)"
    )
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='idx_activity_user_time'),
            models.Index(fields=['content_type', 'object_id'], name='idx_activity_object'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.object_repr} - {self.created_at}"
