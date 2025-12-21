from django.db import models

from django.contrib.auth.models import User

class UserRecovery(models.Model):
    """Model to store hashed recovery tokens for password reset."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recovery')
    token_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recovery token for {self.user.username}"
