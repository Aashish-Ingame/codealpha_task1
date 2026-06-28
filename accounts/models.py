"""
Accounts Models
===============
Custom User model that extends Django's AbstractUser.

WHY extend AbstractUser instead of the default User?
- Django's default User has: username, email, password, first_name, last_name.
- For e-commerce we also need: phone number, full address, etc.
- AbstractUser extension keeps all user data in one table (no JOIN needed),
  and is the Django-recommended approach for new projects.

IMPORTANT: AUTH_USER_MODEL = 'accounts.User' is set in settings.py and
must not be changed after the first migration.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom user with extra e-commerce profile fields.
class User(AbstractUser):
    """
    Custom User model for the StoreHub store.

    Inherits from AbstractUser (username, password, email, is_active, etc.)
    and adds fields specific to e-commerce: full_name, phone, address.
    """

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # ── Identity fields ───────────────────────────────────────────────

    # Single display name instead of separate first/last — more inclusive.
    full_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Customer's full display name",
    )

    # ── Contact & delivery fields ─────────────────────────────────────

    # CharField (not IntegerField) — phone numbers can start with + or 0.
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number (e.g. +91-9876543210)",
    )

    # TextField because addresses can be multi-line.
    address = models.TextField(
        blank=True,
        help_text="Full delivery address",
    )

    # ── Timestamps ────────────────────────────────────────────────────

    # Supplementary timestamp consistent with our other models' naming.
    # AbstractUser already provides date_joined.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the account was created",
    )

    def __str__(self):
        return self.full_name if self.full_name else self.username
