# main/models.py

from django.db import models
from django.conf import settings

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('search', 'Search'),
        ('view', 'View'),
        ('click', 'Click'),
        ('watchlist', 'Add to Watchlist'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    stock_symbol = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.stock_symbol}"
