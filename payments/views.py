import io
import base64
import uuid

import qrcode
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse

from orders.models import Order, OrderItem
from orders.receipt_generator import build_receipt_pdf
from cart.models import Cart
from .models import Payment, UPISettings


# ─────────────────────────────────────────────
# Existing flows (card / cash / wallet)
# ─────────────────────────────────────────────

@login_required
def payment_process_view(request, order_id):
    """Simulate payment processing screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    if order.payment_status == Order.PaymentStatus.PAID:
        messages.info(request, "This order is already paid.")
        return redirect('orders:detail', order_id=order.pk)

    payment = get_object_or_404(Payment, order=order)

    if request.method == 'POST':
        action = request.POST.get('action', 'success')

        if action == 'success':
            with transaction.atomic():
                payment.payment_status = Payment.PaymentStatus.COMPLETED
                payment.save()
                order.payment_status = Order.PaymentStatus.PAID
                order.order_status = Order.OrderStatus.ACCEPTED
                order.save()
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

    context = {'order': order, 'payment': payment}
    return render(request, 'payments/process.html', context)


@login_required
def payment_success_view(request, order_id):
    """Render payment success screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    return render(request, 'payments/success.html', {'order': order})


@login_required
def payment_failure_view(request, order_id):
    """Render payment failure screen."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    return render(request, 'payments/failure.html', {'order': order})


# ─────────────────────────────────────────────
# UPI QR Payment Flow
# ─────────────────────────────────────────────

def _generate_qr_base64(upi_link: str) -> str:
    """Generate a QR code for the given UPI link and return as base64 PNG."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f0f1a", back_color="white").convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


@login_required
def upi_payment_view(request, order_id=None):
    """
    Display the UPI QR payment page.
    Reads live cart total (+ tax) and generates a dynamic QR code.
    Called either directly from cart OR after checkout form selects UPI.
    """
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view')

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view')

    upi_cfg = UPISettings.get_settings()
    subtotal = cart.total_price
    tax = round(subtotal * 5 / 100, 2)
    total = subtotal + tax

    upi_link = (
        f"upi://pay?pa={upi_cfg.upi_id}"
        f"&pn={upi_cfg.merchant_name.replace(' ', '%20')}"
        f"&am={total}"
        f"&cu=INR"
        f"&tn=DineFlow%20Order"
    )

    qr_base64 = _generate_qr_base64(upi_link)

    # Grab delivery info stored by checkout form (if coming from checkout)
    checkout_session = request.session.get('upi_checkout', {})

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('menu_item').all(),
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'upi_id': upi_cfg.upi_id,
        'merchant_name': upi_cfg.merchant_name,
        'upi_link': upi_link,
        'qr_base64': qr_base64,
        'has_checkout_data': bool(checkout_session),
    }
    return render(request, 'payments/upi_payment.html', context)


@login_required
def upi_paid_view(request):
    """
    Handle 'I've Paid' button POST.
    Creates Order, OrderItems, Payment, clears Cart and session, redirects to UPI success.
    """
    if request.method != 'POST':
        return redirect('payments:upi_payment')

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view')

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:view')

    upi_cfg = UPISettings.get_settings()
    subtotal = cart.total_price
    tax = round(subtotal * 5 / 100, 2)
    total = subtotal + tax

    # Prefer checkout session data; fall back to POST body (for direct-from-cart flow)
    checkout_session = request.session.pop('upi_checkout', {})
    delivery_address = (
        checkout_session.get('delivery_address', '')
        or request.POST.get('delivery_address', '').strip()
    )
    special_instructions = (
        checkout_session.get('order_notes', '')
        or request.POST.get('special_instructions', '').strip()
    )

    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            customer=request.user,
            total_amount=total,
            payment_status=Order.PaymentStatus.PENDING,
            order_status=Order.OrderStatus.PENDING,
            delivery_address=delivery_address or None,
            special_instructions=special_instructions or None,
        )

        # Create order items from cart
        for cart_item in cart.items.select_related('menu_item').all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price=cart_item.menu_item.price,
            )

        # Create payment record
        Payment.objects.create(
            order=order,
            amount=total,
            payment_method=Payment.PaymentMethod.UPI,
            payment_status=Payment.PaymentStatus.PENDING_VERIFICATION,
            transaction_id=str(uuid.uuid4()),
        )

        # Clear cart
        cart.items.all().delete()

    messages.success(
        request,
        f"Order #{order.pk} placed! Payment is under verification — we'll confirm shortly."
    )
    return redirect('payments:upi_success', order_id=order.pk)


@login_required
def upi_success_view(request, order_id):
    """Order success page for UPI payments."""
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    payment = get_object_or_404(Payment, order=order)
    context = {
        'order': order,
        'payment': payment,
        'order_items': order.items.select_related('menu_item').all(),
    }
    return render(request, 'payments/upi_success.html', context)


# ─────────────────────────────────────────────
# PDF Receipt Generation
# ─────────────────────────────────────────────

@login_required
def download_receipt_view(request, order_id):
    """
    Generate and stream a PDF receipt for a UPI order.
    Uses the shared DineFlow receipt template (same design as all other modules).
    """
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    try:
        pdf_bytes = build_receipt_pdf(order)
    except Exception as exc:
        messages.error(request, f'Could not generate receipt: {exc}')
        return redirect('payments:upi_success', order_id=order.pk)

    filename = f"DineFlow_Receipt_RST{order.pk:04d}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(pdf_bytes)
    return response
