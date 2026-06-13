from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'order_status', 'payment_status', 'order_date']
    list_filter = ['order_status', 'payment_status', 'order_date']
    search_fields = ['customer__username', 'customer__email']
    list_editable = ['order_status', 'payment_status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_date', 'updated_at']
