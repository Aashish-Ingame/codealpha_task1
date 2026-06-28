"""
Products Models
===============
Product catalogue model for the StoreHub store.

WHY CharField with choices instead of a separate Category model?
For a fixed, small set of categories, CharField choices are simpler:
  - No extra database table or JOINs needed.
  - Categories are version-controlled in code.
  - Easy to reference in templates and filter views.
A separate Category ForeignKey model is preferable when categories
need admin-managed metadata or nested hierarchies.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


# A product available for purchase in the store.
class Product(models.Model):
    """
    Represents a single purchasable item in the catalogue.

    Each product belongs to exactly one category, has a price, stock
    count, optional image, and an average rating.
    Auto-generates a unique URL slug from its name on first save.
    """

    # ── Category constants ────────────────────────────────────────────

    CATEGORY_ELECTRONICS = 'electronics'
    CATEGORY_CLOTHING    = 'clothing'
    CATEGORY_BOOKS       = 'books'
    CATEGORY_HOME        = 'home'
    CATEGORY_SPORTS      = 'sports'
    CATEGORY_BEAUTY      = 'beauty'
    CATEGORY_TOYS        = 'toys'
    CATEGORY_GROCERY     = 'grocery'

    CATEGORY_CHOICES = [
        (CATEGORY_ELECTRONICS, 'Electronics'),
        (CATEGORY_CLOTHING,    'Clothing & Fashion'),
        (CATEGORY_BOOKS,       'Books & Stationery'),
        (CATEGORY_HOME,        'Home & Kitchen'),
        (CATEGORY_SPORTS,      'Sports & Outdoors'),
        (CATEGORY_BEAUTY,      'Beauty & Personal Care'),
        (CATEGORY_TOYS,        'Toys & Games'),
        (CATEGORY_GROCERY,     'Grocery & Gourmet'),
    ]

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    # ── Identity fields ───────────────────────────────────────────────

    name = models.CharField(
        max_length=200,
        help_text="Product title displayed to customers",
    )

    # URL-friendly name auto-generated from `name`; supports SEO-friendly URLs.
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="URL-friendly name (auto-generated from product name)",
    )

    description = models.TextField(
        help_text="Detailed product description",
    )

    # ── Classification & pricing ──────────────────────────────────────

    # db_index speeds up category filter queries.
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text="Product category",
    )

    # DecimalField is mandatory for money — FloatField has precision errors.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        help_text="Product price in your base currency",
    )

    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of units currently available",
    )

    rating = models.FloatField(
        default=0.0,
        help_text="Average customer rating (0.0 to 5.0)",
    )

    # ── Media & visibility ────────────────────────────────────────────

    # Soft-delete flag — deactivated products stay in the DB for order refs.
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive products are hidden from the storefront",
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        default='products/default.jpg',
        help_text="Product image (recommended: 800×800 px)",
    )

    # ── Timestamps ────────────────────────────────────────────────────

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this product was added",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this product was last modified",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate a unique slug from the product name on first save."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        """Return True if at least one unit is available."""
        return self.stock > 0
