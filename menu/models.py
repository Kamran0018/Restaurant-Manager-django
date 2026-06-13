from django.db import models


class Category(models.Model):
    """Food category (e.g., Pizza, Burger, Drinks)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def item_count(self):
        return self.items.filter(availability_status=True).count()


class MenuItem(models.Model):
    """Individual food item on the restaurant menu."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items',
    )
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.PositiveIntegerField(
        help_text='Preparation time in minutes',
        default=15,
    )
    availability_status = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    calories = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - ₹{self.price}'

    @property
    def average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(food_item=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def review_count(self):
        from reviews.models import Review
        return Review.objects.filter(food_item=self).count()
