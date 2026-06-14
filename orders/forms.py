from django import forms


class CheckoutForm(forms.Form):
    """Form for checkout with customer details, delivery address, and payment."""

    # ── Customer Details ──────────────────────────────────────────────────────
    full_name = forms.CharField(
        max_length=300,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. John Doe',
            'id': 'id_full_name',
        }),
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. john@example.com',
            'id': 'id_email',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +91 98765 43210',
            'id': 'id_phone',
        }),
    )

    # ── Delivery Address ──────────────────────────────────────────────────────
    house_number = forms.CharField(
        max_length=50,
        label='House / Flat Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 42-B',
            'id': 'id_house_number',
        }),
    )
    street = forms.CharField(
        max_length=255,
        label='Street / Area',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. MG Road, Koramangala',
            'id': 'id_street',
        }),
    )
    city = forms.CharField(
        max_length=100,
        label='City',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Bengaluru',
            'id': 'id_city',
        }),
    )
    state = forms.CharField(
        max_length=100,
        label='State',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Karnataka',
            'id': 'id_state',
        }),
    )
    pincode = forms.CharField(
        max_length=10,
        label='Pincode',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 560034',
            'id': 'id_pincode',
        }),
    )

    # ── Order Notes ───────────────────────────────────────────────────────────
    order_notes = forms.CharField(
        required=False,
        label='Order Notes',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special instructions, allergies, or requests…',
            'rows': 3,
            'id': 'id_order_notes',
        }),
    )

    # ── Payment Method ────────────────────────────────────────────────────────
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash on Delivery'),
            ('card', 'Credit / Debit Card'),
            ('upi', 'UPI'),
        ],
        label='Payment Method',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        initial='cash',
    )
