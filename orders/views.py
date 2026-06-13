from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart
from payments.models import Payment


@login_required
def checkout_view(request):
    """Display checkout page with order summary and billing form."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('menu_item', 'menu_item__category').all()
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('menu:list')

    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty. Add some items first!')
        return redirect('menu:list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            return _place_order(request, cart, cart_items, form)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with user data
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone or '',
            'address': request.user.address or '',
            'city': request.user.city or '',
            'state': request.user.state or '',
            'zip_code': request.user.zip_code or '',
        })

    subtotal = cart.total_price
    tax = round(subtotal * 5 / 100, 2)
    total = subtotal + tax

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


@transaction.atomic
def _place_order(request, cart, cart_items, form):
    """Create order, order items, payment, and clear cart."""
    subtotal = cart.total_price
    tax = round(subtotal * 5 / 100, 2)
    total = subtotal + tax

    # Build delivery address
    delivery_address = (
        f"{form.cleaned_data['address']}\n"
        f"{form.cleaned_data['city']}, {form.cleaned_data['state']} "
        f"{form.cleaned_data['zip_code']}"
    )

    # Create order
    order = Order.objects.create(
        customer=request.user,
        total_amount=total,
        delivery_address=delivery_address,
        special_instructions=form.cleaned_data.get('special_instructions', ''),
        order_status=Order.OrderStatus.PENDING,
        payment_status=Order.PaymentStatus.PENDING,
    )

    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,
            quantity=cart_item.quantity,
            price=cart_item.menu_item.price,
        )

    # Create payment record
    payment_method = form.cleaned_data.get('payment_method', 'cash')
    payment = Payment.objects.create(
        order=order,
        amount=total,
        payment_method=payment_method,
        payment_status='completed' if payment_method == 'cash' else 'pending',
    )

    # If cash on delivery, mark payment as completed
    if payment_method == 'cash':
        order.payment_status = Order.PaymentStatus.PAID
        order.order_status = Order.OrderStatus.ACCEPTED
        order.save()
        # Clear cart
        cart.items.all().delete()
        messages.success(request, f'Order #{order.pk} placed successfully!')
        return redirect('orders:detail', order_id=order.pk)
    else:
        # For card/upi, redirect to the payment process view without clearing the cart yet
        return redirect('payments:process', order_id=order.pk)


@login_required
def order_detail_view(request, order_id):
    """Display order details and tracking info."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    order_items = order.items.select_related('menu_item').all()

    # Define tracking steps
    tracking_steps = [
        {'key': 'pending', 'label': 'Order Placed', 'icon': 'bi-receipt'},
        {'key': 'accepted', 'label': 'Accepted', 'icon': 'bi-check-circle'},
        {'key': 'preparing', 'label': 'Preparing', 'icon': 'bi-fire'},
        {'key': 'ready', 'label': 'Ready', 'icon': 'bi-box-seam'},
        {'key': 'out_for_delivery', 'label': 'Out for Delivery', 'icon': 'bi-truck'},
        {'key': 'delivered', 'label': 'Delivered', 'icon': 'bi-house-check'},
    ]

    # Determine current step index
    status_order = ['pending', 'accepted', 'preparing', 'ready', 'out_for_delivery', 'delivered']
    current_index = status_order.index(order.order_status) if order.order_status in status_order else -1

    for i, step in enumerate(tracking_steps):
        if i < current_index:
            step['status'] = 'completed'
        elif i == current_index:
            step['status'] = 'active'
        else:
            step['status'] = 'pending'

    context = {
        'order': order,
        'order_items': order_items,
        'tracking_steps': tracking_steps,
        'is_cancelled': order.order_status == 'cancelled',
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_history_view(request):
    """Display all orders for the logged-in user."""
    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related('items__menu_item').order_by('-order_date')

    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def cancel_order_view(request, order_id):
    """Cancel a pending order."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    if order.order_status in ['pending', 'accepted']:
        order.order_status = Order.OrderStatus.CANCELLED
        order.save()

        # Refund payment if exists
        try:
            payment = order.payment
            if payment.payment_status == 'completed':
                payment.payment_status = 'refunded'
                payment.save()
        except Payment.DoesNotExist:
            pass

        messages.info(request, f'Order #{order.pk} has been cancelled.')
    else:
        messages.warning(request, 'This order cannot be cancelled at this stage.')

    return redirect('orders:detail', order_id=order.pk)
