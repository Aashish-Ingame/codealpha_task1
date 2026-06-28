"""
Cart Context Processors
=======================
Injects cart_count into every template context so the navbar badge
can display the number of items without each view passing it manually.
"""

from .models import Cart


def cart_count(request):
    """Return {'cart_count': N} for authenticated users, {'cart_count': 0} otherwise."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return {'cart_count': cart.total_items}
    return {'cart_count': 0}
