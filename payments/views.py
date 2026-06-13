from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from orders.models import Order
from .models import Payment
from cart.models import Cart


@login_required
def payment_process_view(request, order_id):
    """Simulate payment processing screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    # Check if order is already paid or cancelled
    if order.payment_status == Order.PaymentStatus.PAID:
        messages.info(request, "This order is already paid.")
        return redirect('orders:detail', order_id=order.pk)

    payment = get_object_or_404(Payment, order=order)

    if request.method == 'POST':
        action = request.POST.get('action', 'success')

        if action == 'success':
            with transaction.atomic():
                # Update payment
                payment.payment_status = Payment.PaymentStatus.COMPLETED
                payment.save()

                # Update order
                order.payment_status = Order.PaymentStatus.PAID
                order.order_status = Order.OrderStatus.ACCEPTED
                order.save()

                # Clear user's cart
                try:
                    cart = Cart.objects.get(user=request.user)
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    pass

            messages.success(request, f"Payment for Order #{order.pk} completed successfully!")
            return redirect('payments:success', order_id=order.pk)
        else:
            with transaction.atomic():
                payment.payment_status = Payment.PaymentStatus.FAILED
                payment.save()

                order.payment_status = Order.PaymentStatus.FAILED
                order.save()

            messages.error(request, f"Payment for Order #{order.pk} failed. Please try again.")
            return redirect('payments:failure', order_id=order.pk)

    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'payments/process.html', context)


@login_required
def payment_success_view(request, order_id):
    """Render payment success screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    context = {
        'order': order,
    }
    return render(request, 'payments/success.html', context)


@login_required
def payment_failure_view(request, order_id):
    """Render payment failure screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    context = {
        'order': order,
    }
    return render(request, 'payments/failure.html', context)
