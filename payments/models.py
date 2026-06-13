from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    """Payment record for an order."""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash on Delivery'
        CARD = 'card', 'Credit/Debit Card'
        UPI = 'upi', 'UPI'
        WALLET = 'wallet', 'Digital Wallet'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f'Payment #{self.pk} - ₹{self.amount} ({self.payment_status})'
