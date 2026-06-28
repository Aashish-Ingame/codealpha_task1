"""
StoreHub — Root URL Configuration
==================================
All app-level URL routing is delegated to each app's own urls.py via include().
Only root-level pages (landing, home) are wired directly here.

Admin customisation is set here so it applies globally before any request.
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views

# ── Admin branding ────────────────────────────────────────────────────────────
admin.site.site_header = "StoreHub Administration"
admin.site.site_title  = "StoreHub Admin Portal"
admin.site.index_title = "Welcome to the StoreHub Management Dashboard"

# ── URL patterns ──────────────────────────────────────────────────────────────
urlpatterns = [

    # --- Admin ---
    path('admin/', admin.site.urls),

    # --- Root pages ---
    path('',      views.landing_or_redirect, name='landing'),
    path('home/', views.home,                name='home'),

    # --- App URLs ---
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('shop/',     include('products.urls', namespace='products')),
    path('cart/',     include('cart.urls',     namespace='cart')),
    path('orders/',   include('orders.urls',   namespace='orders')),
]

# ── Media files (development only) ───────────────────────────────────────────
# In production, Nginx/Apache serves media directly.
# static() returns [] when DEBUG=False, so this block is safe to leave in.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
