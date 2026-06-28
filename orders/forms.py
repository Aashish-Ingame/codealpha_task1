"""
Orders Forms
============
Forms for the checkout and order processing pipeline.
"""

from django import forms


class CheckoutForm(forms.Form):
    """
    Collects shipping details at checkout.

    Uses a plain Form (not ModelForm) because the fields snapshot into
    the Order model, not the User model. The view pre-fills this form
    from the user's saved profile data.
    """

    shipping_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'}),
    )
    address = forms.CharField(
        label="Street Address",
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '123 Main St...'}),
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'New York'}),
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'NY'}),
    )
    postal_code = forms.CharField(
        max_length=20,
        label="Postal / ZIP Code",
        widget=forms.TextInput(attrs={'placeholder': '10001'}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Contact Phone",
        widget=forms.TextInput(attrs={'placeholder': '+1 555-0198'}),
    )
