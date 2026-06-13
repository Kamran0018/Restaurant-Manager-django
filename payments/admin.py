from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'payment_status', 'transaction_id', 'payment_date']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    search_fields = ['transaction_id', 'order__customer__username']
    readonly_fields = ['transaction_id', 'payment_date']
