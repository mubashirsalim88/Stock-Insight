from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.auth.models import User


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    experience = models.CharField(max_length=100, null=True, blank=True)
    interests = models.TextField(null=True, blank=True)  # Can store comma-separated interests
    trading_knowledge = models.CharField(max_length=50, null=True, blank=True)  # Added field



class UpstoxToken(models.Model):
    access_token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    token_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.access_token[:10]}..."


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    stock_symbol = models.CharField(max_length=10)
    shares = models.IntegerField()
    action = models.CharField(max_length=4)  # 'buy' or 'sell'
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when the object is first created

    def __str__(self):
        return f"{self.action} {self.shares} shares of {self.stock_symbol} at {self.price} on {self.date}"


class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=10)  # Example field, adjust as needed
    shares = models.PositiveIntegerField(default=0)
    average_price = models.DecimalField(max_digits=20, decimal_places=10, default=0)

    class Meta:
        unique_together = ('user', 'stock_symbol') 