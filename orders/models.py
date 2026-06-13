from django.db import models
from django.conf import settings
from menu.models import MenuItem


class Order(models.Model):
    """Customer order."""

    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        PREPARING = 'preparing', 'Preparing'
        READY = 'ready', 'Ready'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out For Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    delivery_address = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-order_date']

    def __str__(self):
        return f'Order #{self.pk} - {self.customer.username}'

    @property
    def status_progress(self):
        """Return progress percentage for tracking bar."""
        progress_map = {
            'pending': 10,
            'accepted': 25,
            'preparing': 50,
            'ready': 70,
            'out_for_delivery': 85,
            'delivered': 100,
            'cancelled': 0,
        }
        return progress_map.get(self.order_status, 0)


class OrderItem(models.Model):
    """Individual item within an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity}x {self.menu_item.name if self.menu_item else "Deleted Item"}'

    @property
    def subtotal(self):
        return self.price * self.quantity
