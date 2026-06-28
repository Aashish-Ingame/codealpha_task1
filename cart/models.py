"""
Cart Models
===========
Database-backed shopping cart: one Cart per user, many CartItems per Cart.

WHY database-backed (not session-based)?
  - Persists across devices and browser sessions.
  - Enables abandoned-cart analytics.
  - Admin can inspect live carts.
"""

from django.conf import settings
from django.db import models


# A shopping cart owned by a single user.
class Cart(models.Model):
    """
    One-to-one cart linked to a registered user.

    A user always has at most one cart; it is created on their first
    "Add to Cart" action via get_or_create().
    """

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    # ── Relationship fields ───────────────────────────────────────────

    # OneToOneField enforces one cart per user at the DB level.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        help_text="The user who owns this cart",
    )

    # ── Timestamps ────────────────────────────────────────────────────

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def total_price(self):
        """Sum of all item subtotals in the cart."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Total unit count across all cart items (e.g. 3× Cable + 1× Phone = 4)."""
        return sum(item.quantity for item in self.items.all())


# A single product line inside a cart.
class CartItem(models.Model):
    """
    One product + quantity pair belonging to a Cart.

    The unique_together constraint prevents duplicate entries for the
    same product in the same cart — the view increments quantity instead.
    """

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')

    # ── Relationship fields ───────────────────────────────────────────

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="The cart this item belongs to",
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        help_text="The product added to the cart",
    )

    # ── Descriptive fields ────────────────────────────────────────────

    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of units of this product",
    )

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"

    @property
    def subtotal(self):
        """Line item total: quantity × current unit price."""
        return self.quantity * self.product.price
