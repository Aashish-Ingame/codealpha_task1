"""
Seed Products Command
=====================
A custom Django management command to populate the database with sample products.

Usage:
    python manage.py seed_products
"""

from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seeds the database with 15 sample products across different categories.'

    def handle(self, *args, **kwargs):
        # We don't want to duplicate products if the command is run twice.
        # We'll check if we already have a good number of products.
        if Product.objects.count() >= 15:
            self.stdout.write(self.style.WARNING('Database already has 15 or more products. Skipping seed.'))
            return

        self.stdout.write('Seeding products...')

        products_data = [
            # Electronics
            {
                'name': 'Wireless Noise Cancelling Headphones',
                'description': 'Premium over-ear headphones with industry-leading noise cancellation and 30-hour battery life.',
                'category': Product.CATEGORY_ELECTRONICS,
                'price': Decimal('299.99'),
                'stock': 45,
                'rating': 4.8,
            },
            {
                'name': '4K Ultra HD Smart TV - 55"',
                'description': 'Stunning 4K resolution with vibrant colors and built-in streaming apps.',
                'category': Product.CATEGORY_ELECTRONICS,
                'price': Decimal('499.00'),
                'stock': 12,
                'rating': 4.5,
            },
            {
                'name': 'Pro Gaming Laptop 15.6"',
                'description': 'High-performance laptop with RTX 4070, 16GB RAM, and 1TB SSD. Ready for VR.',
                'category': Product.CATEGORY_ELECTRONICS,
                'price': Decimal('1499.99'),
                'stock': 8,
                'rating': 4.9,
            },
            {
                'name': 'Smartphone 128GB - Midnight Black',
                'description': 'Latest model smartphone with advanced camera system and all-day battery.',
                'category': Product.CATEGORY_ELECTRONICS,
                'price': Decimal('799.00'),
                'stock': 50,
                'rating': 4.7,
            },
            {
                'name': 'Smartwatch with Heart Rate Monitor',
                'description': 'Track your fitness goals, receive notifications, and monitor your health 24/7.',
                'category': Product.CATEGORY_ELECTRONICS,
                'price': Decimal('199.50'),
                'stock': 25,
                'rating': 4.3,
            },

            # Clothing & Fashion
            {
                'name': 'Classic Men\'s Cotton T-Shirt',
                'description': '100% organic cotton t-shirt. Breathable, comfortable, and perfect for everyday wear.',
                'category': Product.CATEGORY_CLOTHING,
                'price': Decimal('19.99'),
                'stock': 100,
                'rating': 4.2,
            },
            {
                'name': 'Women\'s Denim Jacket',
                'description': 'Vintage wash denim jacket with a relaxed fit. A timeless wardrobe staple.',
                'category': Product.CATEGORY_CLOTHING,
                'price': Decimal('59.99'),
                'stock': 30,
                'rating': 4.6,
            },
            {
                'name': 'Running Shoes - Lightweight Mesh',
                'description': 'Designed for speed and comfort. Features responsive cushioning and breathable mesh upper.',
                'category': Product.CATEGORY_CLOTHING,
                'price': Decimal('89.00'),
                'stock': 40,
                'rating': 4.5,
            },
            {
                'name': 'Leather Wallet - Bifold',
                'description': 'Genuine leather wallet with RFID blocking technology and multiple card slots.',
                'category': Product.CATEGORY_CLOTHING,
                'price': Decimal('34.50'),
                'stock': 60,
                'rating': 4.8,
            },
            {
                'name': 'Winter Beanie Hat',
                'description': 'Warm and cozy knit beanie. One size fits most.',
                'category': Product.CATEGORY_CLOTHING,
                'price': Decimal('14.99'),
                'stock': 120,
                'rating': 4.1,
            },

            # Books & Stationery
            {
                'name': 'The Pragmatic Programmer',
                'description': 'A classic book on software engineering best practices. A must-read for developers.',
                'category': Product.CATEGORY_BOOKS,
                'price': Decimal('39.99'),
                'stock': 20,
                'rating': 4.9,
            },
            {
                'name': 'Premium Hardcover Notebook',
                'description': 'Dotted grid notebook with 120gsm paper, lay-flat binding, and an elastic closure.',
                'category': Product.CATEGORY_BOOKS,
                'price': Decimal('22.00'),
                'stock': 75,
                'rating': 4.7,
            },
            {
                'name': 'Fountain Pen - Fine Nib',
                'description': 'Elegant fountain pen with a smooth writing fine nib. Includes one ink cartridge.',
                'category': Product.CATEGORY_BOOKS,
                'price': Decimal('28.50'),
                'stock': 35,
                'rating': 4.4,
            },
            {
                'name': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'description': 'Learn how to write clean, maintainable, and robust code.',
                'category': Product.CATEGORY_BOOKS,
                'price': Decimal('42.50'),
                'stock': 15,
                'rating': 4.8,
            },
            {
                'name': 'Desk Organizer Set',
                'description': 'Keep your workspace tidy with this stylish 3-piece metal mesh desk organizer.',
                'category': Product.CATEGORY_BOOKS,
                'price': Decimal('18.99'),
                'stock': 50,
                'rating': 4.3,
            },
        ]

        created_count = 0
        for item in products_data:
            # get_or_create prevents duplicates based on the 'name' field
            product, created = Product.objects.get_or_create(
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'category': item['category'],
                    'price': item['price'],
                    'stock': item['stock'],
                    'rating': item['rating'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} products!'))
