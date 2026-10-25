from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add our custom fields to the User edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Business Fields', {
            'fields': ('phone_number', 'role', 'is_biometric_enabled', 
                       'two_factor_enabled', 'failed_login_attempts', 
                       'lockout_until', 'remote_wipe_requested'),
        }),
    )
    
    # Add custom fields to the User creation page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Business Fields', {
            'fields': ('phone_number', 'role'),
        }),
    )
    
    list_display = ('username', 'email', 'phone_number', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
