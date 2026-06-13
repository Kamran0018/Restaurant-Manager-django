from django.db import models
from django.conf import settings


class Reservation(models.Model):
    """Table reservation by a customer."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        NO_SHOW = 'no_show', 'No Show'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
    )
    date = models.DateField()
    time = models.TimeField()
    number_of_guests = models.PositiveIntegerField()
    special_request = models.TextField(blank=True, null=True)
    reservation_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        ordering = ['-date', '-time']

    def __str__(self):
        return f'Reservation by {self.customer.username} on {self.date} at {self.time}'
