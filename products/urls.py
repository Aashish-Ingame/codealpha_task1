"""
Products URLs
=============
URL routing for the product catalogue.

Namespace : products
Prefix    : /shop/   (set in ecommerce/urls.py)
"""

from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [

    # --- Listing ---
    path('',                       views.product_list_view,   name='list'),

    # --- Detail ---
    path('product/<slug:slug>/',   views.product_detail_view, name='detail'),
]
