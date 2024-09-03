# upstox_integration/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Avoid conflicts with Django's default User model
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Avoid conflicts with Django's default User model
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )
    # You can add additional fields here if needed

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    dob = models.DateField(default='2000-01-01')  # Example default value
    gender = models.CharField(max_length=10)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class UpstoxToken(models.Model):
    access_token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    token_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.access_token[:10]}..."
