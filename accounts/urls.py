"""
Accounts URLs
=============
URL routing for user authentication and profile management.

Namespace : accounts
Prefix    : /accounts/   (set in ecommerce/urls.py)
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [

    # --- Auth ---
    path('login/',    views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',   views.logout_view,   name='logout'),

    # --- Profile ---
    path('profile/',  views.profile_view,  name='profile'),

    # --- AJAX ---
    path('check-username/', views.check_username_view, name='check_username'),
]
