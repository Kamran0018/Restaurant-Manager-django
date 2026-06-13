from django.contrib import admin
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_count', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'preparation_time',
        'availability_status', 'is_featured', 'is_vegetarian', 'created_at',
    ]
    list_filter = ['category', 'availability_status', 'is_featured', 'is_vegetarian', 'is_spicy']
    search_fields = ['name', 'description']
    list_editable = ['price', 'availability_status', 'is_featured']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
