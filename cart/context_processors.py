def cart_item_count(request):
    """Context processor to make cart item count available in all templates."""
    count = 0
    if request.user.is_authenticated:
        try:
            from .models import Cart
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            count = 0
    return {'cart_item_count': count}
