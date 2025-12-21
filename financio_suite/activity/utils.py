from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog


def log_activity(user, action, obj, changes=None, request=None):
    """
    Helper function to log user activity.
    
    Args:
        user: User instance
        action: 'create', 'update', 'delete', 'archive', 'activate'
        obj: Model instance being acted upon
        changes: Dict of field changes (optional)
        request: HttpRequest object for IP/user agent (optional)
    
    Returns:
        ActivityLog instance
    """
    content_type = ContentType.objects.get_for_model(obj)
    
    # Get IP address from request
    ip_address = None
    user_agent = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
    
    activity_log = ActivityLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=obj.pk,
        object_repr=str(obj)[:200],  # Limit to 200 chars
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return activity_log


def track_model_changes(old_instance, new_instance, fields_to_track):
    """
    Compare two model instances and return dict of changes.
    
    Args:
        old_instance: Original model instance
        new_instance: Updated model instance
        fields_to_track: List of field names to track
    
    Returns:
        Dict with 'before' and 'after' values for changed fields
    """
    changes = {}
    for field in fields_to_track:
        old_value = getattr(old_instance, field, None)
        new_value = getattr(new_instance, field, None)
        
        # Convert to string for comparison and storage
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None
        
        if old_str != new_str:
            changes[field] = {
                'before': old_str,
                'after': new_str
            }
    
    return changes if changes else None
