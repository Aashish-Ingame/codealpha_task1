"""
Accounts Forms
==============
Custom forms for user registration and profile editing.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Registration form extending Django's built-in UserCreationForm.

    Adds: email (required), full_name, phone, address.
    Password fields and strength validation are handled by the parent class.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'phone', 'address')

    # Make email required (it's optional on the base model).
    email = forms.EmailField(
        required=True,
        help_text="Required. A valid email address.",
    )

    full_name = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required. Your full display name.",
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        help_text="Required. Contact phone number.",
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Required. Your delivery address.",
    )

    def clean_email(self):
        """Reject an email address already registered (case-insensitive)."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        """Persist extra profile fields that UserCreationForm doesn't handle automatically."""
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for editing an existing user's profile.

    Deliberately excludes username and password — those require separate flows.
    """

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_email(self):
        """Ensure the updated email is unique, ignoring the user's own current address."""
        email = self.cleaned_data.get('email')
        if email:
            qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This email address is already in use.")
        return email
