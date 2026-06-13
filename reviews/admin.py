from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'food_item', 'rating', 'review_date']
    list_filter = ['rating', 'review_date']
    search_fields = ['customer__username', 'food_item__name', 'review_text']
    readonly_fields = ['review_date']
