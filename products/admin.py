"""
Products Admin
==============
Django Admin configuration for the Product model.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Customises the Product list and detail views in Django Admin."""

    # ── List view ─────────────────────────────────────────────────────

    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'rating',
        'is_active',
        'image_preview',
    )
    list_filter = (
        'category',
        'is_active',
        'created_at',
    )
    search_fields = (
        'name',
        'description',
    )
    list_editable = (
        'price',
        'stock',
    )
    list_per_page = 25

    # ── Edit / detail view ────────────────────────────────────────────

    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'image_preview_large',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category', 'is_active'),
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'rating'),
        }),
        ('Product Image', {
            'description': (
                'Upload a product image (recommended: 800×800 px, JPEG or PNG). '
                'A preview of the current image is shown below.'
            ),
            'fields': ('image', 'image_preview_large'),
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    # ── Custom columns ────────────────────────────────────────────────

    def image_preview(self, obj):
        """Small 50 px thumbnail shown in the product list table."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;'
                'border-radius:4px;" alt="{}">',
                obj.image.url,
                obj.name,
            )
        return "—"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        """200 px preview rendered on the product edit form."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px;max-width:400px;'
                'object-fit:contain;border-radius:8px;border:1px solid #ddd;'
                'padding:4px;background:#fafafa;" alt="Current image for {}">',
                obj.image.url,
                obj.name,
            )
        return "No image uploaded yet."

    image_preview_large.short_description = 'Current Image'
