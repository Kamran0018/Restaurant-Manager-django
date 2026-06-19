from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Existing card/cash/wallet flows (untouched)
    path('process/<int:order_id>/', views.payment_process_view, name='process'),
    path('success/<int:order_id>/', views.payment_success_view, name='success'),
    path('failure/<int:order_id>/', views.payment_failure_view, name='failure'),

    # New UPI QR flow
    path('upi/', views.upi_payment_view, name='upi_payment'),
    path('upi/paid/', views.upi_paid_view, name='upi_paid'),
    path('upi/success/<int:order_id>/', views.upi_success_view, name='upi_success'),
    path('upi/receipt/<int:order_id>/', views.download_receipt_view, name='upi_receipt'),
]
