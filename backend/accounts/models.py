from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        HELPER = 'HELPER', 'Helper'
        VIEWER = 'VIEWER', 'Viewer'

    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OWNER)
    
    # Security Flags
    is_biometric_enabled = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    remote_wipe_requested = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"