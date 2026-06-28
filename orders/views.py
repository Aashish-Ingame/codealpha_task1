"""
Orders Views
============
Handles the checkout pipeline: cart-to-order conversion with atomic
stock decrement, order confirmation, history, and detail views.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart

from .forms import CheckoutForm
from .models import Order, OrderItem


# ── List views ────────────────────────────────────────────────────────────────

@login_required
def order_history_view(request):
    """List all past orders for the logged-in user, newest first."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


# ── Detail views ──────────────────────────────────────────────────────────────

@login_required
def order_detail_view(request, order_id):
    """Show full details of a specific past order (user-scoped for security)."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'orders/order_detail.html', {'order': order, 'items': items})


@login_required
def order_confirmation_view(request, order_id):
    """Display the success page immediately after a new order is placed."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


# ── Create views ──────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    """
    Display the checkout form and process a new order atomically.

    On POST: validates the shipping form, creates the Order and OrderItems,
    decrements product stock, and clears the cart — all inside a single
    database transaction so any failure rolls everything back cleanly.
    """
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or cart.total_items == 0:
        messages.error(request, "Your cart is empty. Add items before checking out.")
        return redirect('products:list')

    subtotal = cart.total_price
    tax = subtotal * Decimal('0.18')
    shipping = Decimal('50.00')
    grand_total = subtotal + tax + shipping

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        shipping_name=form.cleaned_data['shipping_name'],
                        address=form.cleaned_data['address'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        postal_code=form.cleaned_data['postal_code'],
                        phone=form.cleaned_data['phone'],
                        total_amount=grand_total,
                        status=Order.STATUS_PENDING,
                        payment_status=Order.PAYMENT_PENDING,
                    )

                    for cart_item in cart.items.select_related('product').all():
                        product = cart_item.product
                        if product.stock < cart_item.quantity:
                            raise ValueError(
                                f"Not enough stock for {product.name}. "
                                f"Available: {product.stock}"
                            )
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            unit_price=product.price,
                            quantity=cart_item.quantity,
                        )
                        product.stock -= cart_item.quantity
                        product.save()

                    cart.items.all().delete()

                messages.success(request, f"Order {order.order_number} placed successfully!")
                return redirect('orders:confirmation', order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart:detail')
            except Exception:
                messages.error(
                    request,
                    "An error occurred while processing your order. Please try again.",
                )
                return redirect('cart:detail')
    else:
        form = CheckoutForm(initial={
            'shipping_name': request.user.full_name or request.user.username,
            'phone': request.user.phone,
            'address': request.user.address,
        })

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'grand_total': grand_total,
    })
