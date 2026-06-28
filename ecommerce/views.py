"""
ecommerce/views.py
==================
Root-level views for the project.

Routing:
  /       → anonymous users see the marketing landing page
  /       → authenticated users are redirected to /home/
  /home/  → content-rich home page (deals, bestsellers, new arrivals)
"""

from django.db.models import Count
from django.shortcuts import redirect, render

from products.models import Product


def landing_or_redirect(request):
    """Show the marketing landing page to guests; redirect logged-in users to home."""
    if request.user.is_authenticated:
        return redirect('home')

    featured_products = Product.objects.filter(is_active=True).order_by('-rating')[:4]

    categories = [
        {
            'name': 'Electronics',
            'slug': 'electronics',
            'image_url': 'https://picsum.photos/seed/tech-electronics/800/500',
            'icon': '💻',
        },
        {
            'name': 'Fashion',
            'slug': 'clothing',
            'image_url': 'https://picsum.photos/seed/fashion-clothing/800/500',
            'icon': '👗',
        },
        {
            'name': 'Books & Stationery',
            'slug': 'books',
            'image_url': 'https://picsum.photos/seed/books-stationery/800/500',
            'icon': '📚',
        },
    ]

    return render(request, 'landing.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def home(request):
    """Display the Amazon-style home page with categories, deals, bestsellers, and new arrivals."""
    category_icons = {
        'electronics': 'ti-device-laptop',
        'clothing':    'ti-hanger',
        'books':       'ti-book',
        'home':        'ti-home',
        'sports':      'ti-ball-football',
        'beauty':      'ti-stars',
        'toys':        'ti-horse-toy',
        'grocery':     'ti-shopping-cart',
    }
    cat_choices = dict(Product.CATEGORY_CHOICES)

    categories_raw = (
        Product.objects
        .filter(is_active=True)
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    categories = [
        {
            'id': c['category'],
            'name': cat_choices.get(c['category'], c['category'].title()),
            'count': c['count'],
            'icon': category_icons.get(c['category'], 'ti-box'),
        }
        for c in categories_raw
    ]

    deals       = Product.objects.filter(is_active=True).order_by('price')[:6]
    bestsellers = Product.objects.filter(is_active=True).order_by('-rating')[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, 'home.html', {
        'categories': categories,
        'deals': deals,
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'spotlights': categories[:2] if len(categories) >= 2 else categories,
    })
