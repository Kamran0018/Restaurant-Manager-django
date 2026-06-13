from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.payment_process_view, name='process'),
    path('success/<int:order_id>/', views.payment_success_view, name='success'),
    path('failure/<int:order_id>/', views.payment_failure_view, name='failure'),
]
