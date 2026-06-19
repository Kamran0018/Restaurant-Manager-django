from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, UPISettings


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'payment_status', 'transaction_id', 'payment_date']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    search_fields = ['transaction_id', 'order__customer__username']
    readonly_fields = ['transaction_id', 'payment_date']


@admin.register(UPISettings)
class UPISettingsAdmin(admin.ModelAdmin):
    """Singleton admin — always edits record #1."""
    list_display = ['upi_id', 'merchant_name', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one record
        return not UPISettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect the changelist straight to the single edit form."""
        from django.shortcuts import redirect
        obj, _ = UPISettings.objects.get_or_create(pk=1)
        return redirect(f'/admin/payments/upisettings/{obj.pk}/change/')
