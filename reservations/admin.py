from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date', 'time', 'number_of_guests', 'reservation_status', 'created_at']
    list_filter = ['reservation_status', 'date']
    search_fields = ['customer__username', 'customer__email']
    list_editable = ['reservation_status']
