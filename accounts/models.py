from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model with additional fields for restaurant management."""

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        MANAGER = 'manager', 'Restaurant Manager'
        ADMIN = 'admin', 'Administrator'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default='profile_pics/default.png',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name() or self.username}'

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN
