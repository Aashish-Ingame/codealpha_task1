"""
Accounts Views
==============
Handles user registration, login, logout, profile editing,
and AJAX helpers (username availability check).

Navigation flow:
  Register → auto-login → /accounts/profile/  (welcome toast)
  Login    → ?next= URL or /shop/
  Logout   → /  (landing page)
  @login_required redirects → /accounts/login/?next={url}
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from orders.models import Order

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import User


# ── Registration ──────────────────────────────────────────────────────────────

def register_view(request):
    """Handle user registration and auto-login on success."""
    if request.user.is_authenticated:
        return redirect('products:list')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to StoreHub, {user.full_name or user.username}! "
                "Your account is ready.",
            )
            return redirect('accounts:profile')

        messages.error(request, "Please fix the errors below to continue.")
        return render(request, 'accounts/auth.html', {
            'register_form': form,
            'login_form': AuthenticationForm(),
            'default_tab': 'signup',
        })

    return render(request, 'accounts/auth.html', {
        'register_form': CustomUserCreationForm(),
        'login_form': AuthenticationForm(),
        'default_tab': 'signup',
    })


# ── Login ─────────────────────────────────────────────────────────────────────

def login_view(request):
    """Authenticate the user and redirect to ?next= or /shop/."""
    if request.user.is_authenticated:
        return redirect('products:list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name or user.username}!")
            next_url = request.GET.get('next', '').strip()
            return redirect(next_url) if next_url else redirect('products:list')

        messages.error(request, "Incorrect username or password. Please try again.")
        return render(request, 'accounts/auth.html', {
            'login_form': form,
            'register_form': CustomUserCreationForm(),
            'default_tab': 'login',
        })

    return render(request, 'accounts/auth.html', {
        'login_form': AuthenticationForm(),
        'register_form': CustomUserCreationForm(),
        'default_tab': 'login',
    })


# ── Logout ────────────────────────────────────────────────────────────────────

def logout_view(request):
    """Log the user out (POST only) and redirect to the landing page."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    logout(request)
    messages.info(request, "You've been logged out. See you next time!")
    return redirect('home')


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    """Display and save inline edits to the user's profile and order history."""
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')

        messages.error(request, "Please correct the errors below.")
        orders = Order.objects.filter(user=user).order_by('-created_at')
        return render(request, 'accounts/profile.html', {
            'profile_form': form,
            'orders': orders,
            'edit_mode': True,
        })

    form = ProfileUpdateForm(instance=user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {
        'profile_form': form,
        'orders': orders,
        'edit_mode': False,
    })


# ── AJAX helpers ──────────────────────────────────────────────────────────────

@require_GET
def check_username_view(request):
    """Return JSON indicating whether a username is available (case-insensitive)."""
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'available': False})

    taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'available': not taken})
