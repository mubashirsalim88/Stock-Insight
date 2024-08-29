from django.contrib import admin
from django.urls import path
from main import views
from upstox_integration import views
from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home,name='home'),
    path('profile', profile,name='profile'),
    path('real-time-charts/', views.real_time_charts, name='real_time_charts'),
    path('upstox/authorize/', views.upstox_authorize, name='upstox_authorize'),
    path('upstox/callback/', views.upstox_callback, name='upstox_callback'),
    path('fetch-historical-data/', views.fetch_historical_data, name='fetch_historical_data'),
    path('fetch-historical-data/<str:stock_symbol>/', views.fetch_historical_data, name='fetch_historical_data'),
]