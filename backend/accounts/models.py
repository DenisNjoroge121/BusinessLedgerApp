from datetime import timedelta
from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from django.conf import settings

# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        HELPER = "HELPER", "Helper"
        VIEWER = "VIEWER", "Viewer"

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="members", null=True, blank=True
    )
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OWNER)
    two_factor_enabled = models.BooleanField(default=False)
    failed_login_attempts= models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    remote_wipe_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_locked(self):
        return bool(self.lockout_until and self.lockout_until > timezone.now())

    def register_failed_attempt(self):
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=self.pk)
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.LOCKOUT_MAX_ATTEMPTS:
                user.lockout_until = timezone.now() + timedelta(minutes=settings.LOCKOUT_MINUTES)
                user.failed_login_attempts = 0
            user.save(update_fields=["failed_login_attempts", "lockout_until"])

    def reset_attempts(self):
        if self.failed_login_attempts or self.lockout_until:
            self.failed_login_attempts = 0
            self.lockout_until= None
            self.save(update_fields=["failed_login_attempts", "lockout_until"])