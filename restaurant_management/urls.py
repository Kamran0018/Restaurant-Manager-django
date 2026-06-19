"""
URL configuration for restaurant_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('reservations/', include('reservations.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site header
admin.site.site_header = 'DineFlow Admin'
admin.site.site_title = 'DineFlow Admin Portal'
admin.site.index_title = 'Welcome to DineFlow Management'
