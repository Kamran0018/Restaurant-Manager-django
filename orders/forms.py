from django import forms


class CheckoutForm(forms.Form):
    """Form for checkout with billing and delivery details."""

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        }),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Full Delivery Address',
            'rows': 3,
        }),
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        }),
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
        }),
    )
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP Code',
        }),
    )
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special instructions for your order?',
            'rows': 2,
        }),
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash on Delivery'),
            ('card', 'Credit/Debit Card'),
            ('upi', 'UPI'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        initial='cash',
    )
