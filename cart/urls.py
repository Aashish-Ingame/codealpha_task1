"""
Cart URLs
=========
URL routing for shopping cart operations.

Namespace : cart
Prefix    : /cart/   (set in ecommerce/urls.py)
"""

from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [

    # --- View ---
    path('',                        views.cart_detail_view,          name='detail'),

    # --- Actions ---
    path('add/<int:product_id>/',   views.add_to_cart_view,          name='add'),
    path('update/<int:item_id>/',   views.update_cart_quantity_view, name='update'),
    path('remove/<int:item_id>/',   views.remove_from_cart_view,     name='remove'),
    path('clear/',                  views.clear_cart_view,           name='clear'),
]
