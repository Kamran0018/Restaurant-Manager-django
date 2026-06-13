from django.shortcuts import render
from menu.models import MenuItem, Category


def home_view(request):
    """Home page with featured dishes and restaurant info."""
    featured_items = MenuItem.objects.filter(
        availability_status=True
    ).order_by('-created_at')[:6]
    categories = Category.objects.all()[:6]

    context = {
        'featured_items': featured_items,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About page."""
    return render(request, 'core/about.html')


def contact_view(request):
    """Contact page."""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # TODO: Send email notification
        from django.contrib import messages as msg
        msg.success(request, 'Thank you for your message! We\'ll get back to you soon.')
    return render(request, 'core/contact.html')
