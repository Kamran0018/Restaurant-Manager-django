from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_list_view, name='list'),
    path('book/', views.reservation_create_view, name='create'),
    path('<int:pk>/', views.reservation_detail_view, name='detail'),
    path('<int:pk>/cancel/', views.reservation_cancel_view, name='cancel'),
]
