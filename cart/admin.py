"""
Cart Admin
==========
Registers Cart and CartItem models with Django Admin.
CartItems are displayed inline inside the Cart edit page.
"""

from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Compact tabular display of cart items inside the Cart admin page."""

    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        """Computed line-item total."""
        return obj.subtotal

    subtotal.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin view for Carts with inline CartItems."""

    list_display = (
        'user',
        'total_items',
        'total_price',
        'updated_at',
    )
    list_filter = ('created_at',)
    search_fields = (
        'user__username',
        'user__email',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    inlines = [CartItemInline]

    def total_items(self, obj):
        """Total unit count across all cart items."""
        return obj.total_items

    total_items.short_description = 'Items'

    def total_price(self, obj):
        """Sum of all item subtotals."""
        return obj.total_price

    total_price.short_description = 'Total'
