from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from menu.models import MenuItem


@login_required
def cart_view(request):
    """Display the user's shopping cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('menu_item', 'menu_item__category').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, item_id):
    """Add a menu item to the cart."""
    menu_item = get_object_or_404(MenuItem, pk=item_id, availability_status=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': 1},
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{menu_item.name} added to cart!',
            'cart_count': cart.total_items,
            'cart_total': str(cart.total_price),
        })

    messages.success(request, f'{menu_item.name} has been added to your cart!')
    return redirect(request.META.get('HTTP_REFERER', 'menu:list'))


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Update quantity of a cart item."""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    action = request.POST.get('action', '')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
            return redirect('cart:view')
    elif action == 'set':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'subtotal': str(cart_item.subtotal),
            'cart_total': str(cart.total_price),
            'cart_count': cart.total_items,
        })

    return redirect('cart:view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item_name = cart_item.menu_item.name
    cart = cart_item.cart
    cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{item_name} removed from cart.',
            'cart_total': str(cart.total_price),
            'cart_count': cart.total_items,
        })

    messages.info(request, f'{item_name} has been removed from your cart.')
    return redirect('cart:view')


@login_required
@require_POST
def clear_cart(request):
    """Clear all items from the cart."""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared.',
            'cart_total': '0',
            'cart_count': 0,
        })

    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart:view')
