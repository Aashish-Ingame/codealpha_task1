"""
Orders Admin
============
Django Admin configuration for Order and OrderItem models.
OrderItems are shown inline inside the Order detail page.
"""

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Read-only tabular view of line items inside the Order admin page."""

    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        'product',
        'product_name',
        'unit_price',
        'quantity',
        'subtotal',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin view for Orders with inline OrderItems and a bulk 'mark as shipped' action."""

    list_display = (
        'order_number',
        'user',
        'total_amount',
        'status',
        'payment_status',
        'created_at',
    )
    list_filter = (
        'status',
        'payment_status',
        'created_at',
    )
    search_fields = (
        'order_number',
        'user__username',
        'user__email',
        'shipping_name',
    )
    list_editable = ('status',)
    readonly_fields = (
        'order_number',
        'user',
        'total_amount',
        'created_at',
    )
    inlines = [OrderItemInline]
    actions = ['mark_as_shipped']

    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'user',
                'status',
                'payment_status',
                'total_amount',
                'created_at',
            ),
        }),
        ('Shipping Details', {
            'fields': (
                'shipping_name',
                'phone',
                'address',
                'city',
                'state',
                'postal_code',
            ),
        }),
    )

    def mark_as_shipped(self, request, queryset):
        """Bulk action — set selected orders to Shipped status."""
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f"{updated} order(s) successfully marked as Shipped.")

    mark_as_shipped.short_description = "Mark selected orders as Shipped"
