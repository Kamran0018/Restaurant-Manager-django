from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User


class CustomerRegistrationForm(UserCreationForm):
    """Registration form for new customers."""

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        }),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        }),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        }),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        }),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        if commit:
            user.save()
        return user


class CustomerLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'profile_picture',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """Password reset form with Bootstrap styling."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
        }),
    )
