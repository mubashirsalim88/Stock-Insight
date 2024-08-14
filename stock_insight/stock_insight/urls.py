from django.contrib import admin
from django.urls import path
from main import views
from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home,name='home'),
    path('profile', profile,name='profile')
    path('premium_alerts', premium_alerts,name='premium_alerts')
]
