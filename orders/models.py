"""
Orders Models
=============
Order and OrderItem models representing completed purchases.

KEY DESIGN DECISIONS:
1. Shipping address is stored directly on Order (not a FK to an Address
   model) so past orders always show the original delivery address even
   if the user later changes their profile.

2. OrderItem stores product_name and unit_price as snapshot fields (not
   just a FK to Product) so order totals remain accurate even if a
   product is renamed, repriced, or deleted.
"""

import uuid

from django.conf import settings
from django.db import models


# A completed customer order — an immutable financial record.
class Order(models.Model):
    """
    Represents a placed order with snapshotted shipping address and total.

    Lifecycle: Pending → Processing → Shipped → Delivered (or Cancelled).
    """

    # ── Status constants ──────────────────────────────────────────────

    STATUS_PENDING    = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED    = 'shipped'
    STATUS_DELIVERED  = 'delivered'
    STATUS_CANCELLED  = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED,    'Shipped'),
        (STATUS_DELIVERED,  'Delivered'),
        (STATUS_CANCELLED,  'Cancelled'),
    ]

    PAYMENT_PENDING   = 'pending'
    PAYMENT_COMPLETED = 'completed'
    PAYMENT_FAILED    = 'failed'

    PAYMENT_CHOICES = [
        (PAYMENT_PENDING,   'Pending'),
        (PAYMENT_COMPLETED, 'Completed'),
        (PAYMENT_FAILED,    'Failed'),
    ]

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    # ── Identity fields ───────────────────────────────────────────────

    # Human-readable unique identifier; auto-generated in save().
    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Unique order identifier (auto-generated)",
    )

    # ── Relationship fields ───────────────────────────────────────────

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The customer who placed this order",
    )

    # ── Snapshotted shipping address ──────────────────────────────────

    shipping_name = models.CharField(max_length=150, help_text="Recipient's full name")
    address       = models.TextField(help_text="Street address for delivery")
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    postal_code   = models.CharField(max_length=20, help_text="ZIP or postal code")
    phone         = models.CharField(max_length=20, help_text="Contact phone for delivery")

    # ── Order details ─────────────────────────────────────────────────

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Grand total charged to the customer",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_PENDING,
    )

    # ── Timestamps ────────────────────────────────────────────────────

    created_at = models.DateTimeField(auto_now_add=True, help_text="When the order was placed")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Auto-generate a unique order number (format: ORD-XXXXXXXX) on first save."""
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            while Order.objects.filter(order_number=self.order_number).exists():
                self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


# A snapshotted line item belonging to an order.
class OrderItem(models.Model):
    """
    One product line within an Order, with price and name frozen at purchase time.

    product_name and unit_price are stored separately so the order record
    remains accurate even if the product is later updated or deleted.
    """

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    # ── Relationship fields ───────────────────────────────────────────

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    # SET_NULL: if a product is deleted, keep the order item with its snapshot data.
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )

    # ── Snapshotted product data ──────────────────────────────────────

    product_name = models.CharField(
        max_length=200,
        help_text="Product name at time of purchase",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of purchase",
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"

    @property
    def subtotal(self):
        """Line item total using the snapshotted unit_price (not the current product price)."""
        return self.quantity * self.unit_price
