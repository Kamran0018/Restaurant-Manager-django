from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from menu.models import MenuItem


class Review(models.Model):
    """Customer review for a food item."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    food_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review_text = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-review_date']
        unique_together = ['customer', 'food_item']

    def __str__(self):
        return f'{self.customer.username} - {self.food_item.name} ({self.rating}★)'
