# myproject/urls.py

from django.contrib import admin
from django.urls import path
from main import views as main_views  # Import views from the correct app
from upstox_integration import views as upstox_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),  # Main app home view
    path('profile/', main_views.profile, name='profile'),  # Main app profile view
    path('market_today/', main_views.market_today, name='market_today'),  # Main app market_today view
    path('real-time-charts/', upstox_views.real_time_charts, name='real_time_charts'),  # Upstox integration view
    path('upstox/authorize/', upstox_views.upstox_authorize, name='upstox_authorize'),  # Upstox integration view
    path('upstox/callback/', upstox_views.upstox_callback, name='upstox_callback'),  # Upstox integration view
    path('fetch-historical-data/', upstox_views.fetch_historical_data, name='fetch_historical_data'),  # Upstox integration view
    path('fetch-historical-data/<str:stock_symbol>/', upstox_views.fetch_historical_data, name='fetch_historical_data'),  # Upstox integration view
    path('register/', main_views.register, name='register'),  # Main app register view
    path('login/', main_views.login, name='login'),  # Main app login view
    path('logout/', main_views.logout, name='logout'), # Logout URL
]
