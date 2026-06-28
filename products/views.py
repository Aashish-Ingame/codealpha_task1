"""
Products Views
==============
Handles the product catalogue: listing with search/filter/sort,
and individual product detail pages.
"""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product


def product_list_view(request):
    """Display all active products with search, filter, sort, and pagination."""
    queryset = Product.objects.filter(is_active=True)

    # Search by name or description.
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Filter by category.
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)

    # Filter by price range.
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.replace('.', '', 1).isdigit():
        queryset = queryset.filter(price__gte=min_price)
    if max_price and max_price.replace('.', '', 1).isdigit():
        queryset = queryset.filter(price__lte=max_price)

    # Sort — falls back to model Meta.ordering ('-created_at') when unset.
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_desc':
        queryset = queryset.order_by('-price')

    paginator = Paginator(queryset, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': Product.CATEGORY_CHOICES,
        'current_query': query or '',
        'current_category': category or '',
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_sort': sort_by or '',
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """Display full details for a single active product."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    max_qty = min(product.stock, 10)
    quantity_range = range(1, max_qty + 1) if max_qty > 0 else []

    return render(request, 'products/product_detail.html', {
        'product': product,
        'quantity_range': quantity_range,
    })
