from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, MenuItem


def menu_list_view(request):
    """Display menu with search and category filters."""
    categories = Category.objects.filter(is_active=True)
    items = MenuItem.objects.filter(availability_status=True).select_related('category')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        items = items.filter(category_id=category_id)

    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # Sort
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        items = items.order_by('price')
    elif sort_by == 'price_high':
        items = items.order_by('-price')
    elif sort_by == 'name':
        items = items.order_by('name')
    elif sort_by == 'newest':
        items = items.order_by('-created_at')

    # Vegetarian filter
    is_veg = request.GET.get('veg', '')
    if is_veg:
        items = items.filter(is_vegetarian=True)

    context = {
        'categories': categories,
        'items': items,
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    return render(request, 'menu/menu_list.html', context)


def menu_detail_view(request, pk):
    """Display individual menu item details."""
    item = get_object_or_404(MenuItem, pk=pk, availability_status=True)
    related_items = MenuItem.objects.filter(
        category=item.category,
        availability_status=True,
    ).exclude(pk=pk)[:4]

    context = {
        'item': item,
        'related_items': related_items,
    }
    return render(request, 'menu/menu_detail.html', context)
