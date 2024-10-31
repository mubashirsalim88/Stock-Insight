from django.contrib import admin
from .models import Portfolio, Transaction, StockData

admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(StockData)
