"""
Accounts Admin
==============
Registers the custom User model with Django Admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Extends the default UserAdmin to surface our extra profile fields."""

    model = User

    list_display = (
        'username',
        'email',
        'full_name',
        'phone',
        'date_joined',
    )
    search_fields = (
        'username',
        'email',
        'phone',
    )
    readonly_fields = (
        'date_joined',
        'last_login',
        'created_at',
    )

    # Append our custom fields to the existing fieldsets from UserAdmin.
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('full_name', 'phone', 'address'),
        }),
    )
