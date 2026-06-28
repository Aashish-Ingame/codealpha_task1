"""
Cart Views
==========
Handles all shopping cart operations: viewing, adding, updating,
removing items, and clearing the cart. All views require login.
"""

import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import Cart, CartItem


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_or_create_cart(user):
    """Return the user's cart, creating it if it does not yet exist."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _cart_totals(cart):
    """Return a dict of recalculated subtotal, tax, shipping, and grand total."""
    subtotal = cart.total_price
    tax = subtotal * Decimal('0.18')
    shipping = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    return {
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'grand_total': subtotal + tax + shipping,
    }


# ── List / detail views ───────────────────────────────────────────────────────

@login_required
def cart_detail_view(request):
    """Display the user's cart with subtotal, 18% GST, flat shipping, and grand total."""
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('product').all()
    totals = _cart_totals(cart)

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'items': items,
        **totals,
    })


# ── Add / create views ────────────────────────────────────────────────────────

@login_required
@require_POST
def add_to_cart_view(request, product_id):
    """Add a product to the cart, or increment its quantity if already present."""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('products:detail', slug=product.slug)

    if quantity > product.stock:
        messages.error(
            request,
            f"Sorry, only {product.stock} units of {product.name} are available.",
        )
        return redirect('products:detail', slug=product.slug)

    cart = _get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity},
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.warning(
                request,
                f"You can't add more of {product.name}. Stock limit reached.",
            )
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated quantity of {product.name} in your cart.")
    else:
        messages.success(request, f"Added {product.name} to your cart.")

    return redirect('cart:detail')


# ── Update views ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def update_cart_quantity_view(request, item_id):
    """AJAX endpoint — update a cart item's quantity and return recalculated totals."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    try:
        data = json.loads(request.body)
        new_quantity = int(data.get('quantity', 1))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

    if new_quantity < 0:
        return JsonResponse(
            {'success': False, 'error': 'Quantity cannot be negative'}, status=400
        )

    if new_quantity == 0:
        cart_item.delete()
        cart = cart_item.cart
        totals = _cart_totals(cart)
        return JsonResponse({
            'success': True,
            'item_removed': True,
            'item_subtotal': '0.00',
            'cart_subtotal': str(totals['subtotal']),
            'tax': str(totals['tax']),
            'shipping': str(totals['shipping']),
            'grand_total': str(totals['grand_total']),
            'cart_count': cart.total_items,
        })

    if new_quantity > cart_item.product.stock:
        return JsonResponse(
            {'success': False, 'error': f'Only {cart_item.product.stock} available'},
            status=400,
        )

    cart_item.quantity = new_quantity
    cart_item.save()

    cart = cart_item.cart
    totals = _cart_totals(cart)
    return JsonResponse({
        'success': True,
        'item_subtotal': str(cart_item.subtotal),
        'cart_subtotal': str(totals['subtotal']),
        'tax': str(totals['tax']),
        'shipping': str(totals['shipping']),
        'grand_total': str(totals['grand_total']),
        'cart_count': cart.total_items,
    })


# ── Delete / remove views ─────────────────────────────────────────────────────

@login_required
@require_POST
def remove_from_cart_view(request, item_id):
    """Remove a single item from the cart entirely."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"Removed {product_name} from your cart.")
    return redirect('cart:detail')


@login_required
@require_POST
def clear_cart_view(request):
    """Remove all items from the user's cart."""
    cart = _get_or_create_cart(request.user)
    cart.items.all().delete()
    messages.info(request, "Your cart has been cleared.")
    return redirect('cart:detail')
