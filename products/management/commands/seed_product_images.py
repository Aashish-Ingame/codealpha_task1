"""
Seed Product Images Command
============================
Downloads a real photo from Lorem Picsum (https://picsum.photos) for every
product that doesn't already have a saved image, and stores it via Django's
ImageField so it appears immediately in the storefront and admin.

Usage:
    python manage.py seed_product_images           # skips products that already have images
    python manage.py seed_product_images --force   # re-downloads images for ALL products

How it works:
    Lorem Picsum returns a deterministic 600×600 JPEG for each unique seed string.
    We use the product slug as the seed so the same product always gets the same
    image (idempotent re-runs).  We also use category-specific integer offsets to
    ensure Electronics gets a different-looking image than Clothing, etc.
"""

import urllib.request
import urllib.error

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from products.models import Product


# ── Category → Picsum seed offset ────────────────────────────────────────────
# Lorem Picsum images are fetched via https://picsum.photos/seed/<seed>/600/600
# Using category-keyed prefixes makes products of the same category look thematically
# similar (same area of the Picsum image set).
CATEGORY_SEED_PREFIX = {
    Product.CATEGORY_ELECTRONICS: 'tech',
    Product.CATEGORY_CLOTHING:    'fashion',
    Product.CATEGORY_BOOKS:       'books',
    Product.CATEGORY_HOME:        'home',
    Product.CATEGORY_SPORTS:      'sport',
    Product.CATEGORY_BEAUTY:      'beauty',
    Product.CATEGORY_TOYS:        'toy',
    Product.CATEGORY_GROCERY:     'food',
}

# Image dimensions to download
IMG_WIDTH  = 600
IMG_HEIGHT = 600

# Timeout for each HTTP request (seconds)
REQUEST_TIMEOUT = 15


class Command(BaseCommand):
    help = (
        'Downloads a real photo from Lorem Picsum for every product that does '
        'not yet have an image, and saves it to the product\'s image field.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-download and overwrite images for ALL products, even those that already have one.',
        )

    def handle(self, *args, **options):
        force   = options['force']
        products = Product.objects.all().order_by('name')

        if not products.exists():
            self.stdout.write(self.style.WARNING(
                'No products found in the database. '
                'Run "python manage.py seed_products" first.'
            ))
            return

        total    = products.count()
        added    = 0
        skipped  = 0
        failed   = 0

        self.stdout.write(f'\nProcessing {total} product(s)…\n')

        for product in products:
            # ── Skip products that already have a real saved image ──────────
            already_has_image = (
                product.image
                and product.image.name          # field is not empty string
                and product.image.name != 'products/default.jpg'  # not just the default
            )

            if already_has_image and not force:
                self.stdout.write(
                    self.style.WARNING(f'  [SKIP]  {product.name} — already has an image')
                )
                skipped += 1
                continue

            # ── Build the Picsum URL ─────────────────────────────────────────
            category_prefix = CATEGORY_SEED_PREFIX.get(product.category, 'product')
            # Combine category prefix + slug for a unique, stable, category-appropriate seed
            seed = f'{category_prefix}-{product.slug}'
            url  = f'https://picsum.photos/seed/{seed}/{IMG_WIDTH}/{IMG_HEIGHT}'

            # ── Download the image ───────────────────────────────────────────
            self.stdout.write(f'  [GET]   {product.name}')
            self.stdout.write(f'          {url}')

            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Django-StoreHub/1.0 (product image seed)'},
                )
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                    image_data = response.read()

            except urllib.error.URLError as exc:
                self.stdout.write(
                    self.style.ERROR(f'  [FAIL]  Could not download image — {exc.reason}')
                )
                failed += 1
                continue
            except Exception as exc:  # noqa: BLE001
                self.stdout.write(
                    self.style.ERROR(f'  [FAIL]  Unexpected error — {exc}')
                )
                failed += 1
                continue

            # ── Save to the ImageField via ContentFile ──────────────────────
            # ContentFile wraps raw bytes so Django can treat them as a file upload.
            # The filename becomes the basename inside MEDIA_ROOT/products/.
            filename = f'{product.slug}.jpg'
            content  = ContentFile(image_data, name=filename)

            product.image.save(filename, content, save=True)

            self.stdout.write(
                self.style.SUCCESS(f'  [OK]    Added image for: {product.name}')
            )
            added += 1

        # ── Summary ─────────────────────────────────────────────────────────
        separator = '-' * 56
        self.stdout.write('\n' + separator)
        self.stdout.write(self.style.SUCCESS(f'  Done! Added: {added}'))
        if skipped:
            self.stdout.write(self.style.WARNING(f'  Skipped (already had image): {skipped}'))
        if failed:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed}'))
        self.stdout.write(separator + '\n')
