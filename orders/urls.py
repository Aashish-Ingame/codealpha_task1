"""
Orders URLs
===========
URL routing for the checkout pipeline and order management.

Namespace : orders
Prefix    : /orders/   (set in ecommerce/urls.py)
"""

from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [

    # --- Checkout ---
    path('checkout/',                    views.checkout_view,            name='checkout'),

    # --- Confirmation ---
    path('confirmation/<int:order_id>/', views.order_confirmation_view,  name='confirmation'),

    # --- History ---
    path('history/',                     views.order_history_view,       name='history'),
    path('<int:order_id>/',              views.order_detail_view,        name='detail'),
]
