from django.contrib import admin
from django.urls import path
from main import views as main_views  # Import views from the correct app
from upstox_integration import views as upstox_views
from technical_analysis import views as ta_views  # Import views from technical_analysis app

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main App URLs
    path('', main_views.home, name='home'),  # Main app home view
    path('profile/', main_views.profile, name='profile'),  # Main app profile view
    path('market_today/', main_views.market_today, name='market_today'),  # Main app market_today view
    path('register/', main_views.register, name='register'),  # Main app register view
    path('login/', main_views.login, name='login'),  # Main app login view
    path('logout/', main_views.logout, name='logout'),  # Main app logout view
    
    # Upstox Integration URLs
    path('recommendations/', upstox_views.recommendations, name='recommendations'),  # Recommendations view
    path('real-time-charts/', upstox_views.real_time_charts, name='real_time_charts'),  # Real-time charts view
    path('upstox/authorize/', upstox_views.upstox_authorize, name='upstox_authorize'),  # Upstox authorize view
    path('upstox/callback/', upstox_views.upstox_callback, name='upstox_callback'),  # Upstox callback view
    path('fetch-historical-data/', upstox_views.fetch_historical_data, name='fetch_historical_data'),  # Fetch historical data view
    path('fetch-historical-data/<str:stock_symbol>/', upstox_views.fetch_historical_data, name='fetch_historical_data_with_symbol'),  # Fetch historical data for specific stock
    
   path('technical-analysis/', ta_views.landing_page, name='technical_analysis_landing'),  # Landing Page
    path('technical-analysis/stock-market/', ta_views.slide_stock_market, name='slide_stock_market'),  # Stock Market Intro
    path('technical-analysis/other-markets/', ta_views.slide_other_markets, name='slide_other_markets'),  # Other Markets
    path('technical-analysis/trading-vs-investing/', ta_views.slide_trading_vs_investing, name='slide_trading_vs_investing'),  # Trading vs Investing
    path('technical-analysis/technical-analysis-charts/', ta_views.slide_technical_analysis_charts, name='slide_technical_analysis_charts'),  # Technical Analysis - Charts
    path('technical-analysis/price-action/', ta_views.slide_price_action, name='slide_price_action'),  # Price Action
    path('technical-analysis/support-resistance/', ta_views.slide_support_resistance, name='slide_support_resistance'),  # Support and Resistance
    path('technical-analysis/trendlines/', ta_views.slide_trendlines, name='slide_trendlines'),  # Trendlines Intro
    path('technical-analysis/other-price-action/', ta_views.slide_other_price_action, name='slide_other_price_action'),  # Other Price Action Techniques
    path('technical-analysis/indicators/', ta_views.slide_indicators, name='slide_indicators'),  # Indicators (MACD, RSI)
    path('technical-analysis/candlesticks/', ta_views.slide_candlesticks, name='slide_candlesticks'),  # Candlestick Patterns
    path('technical-analysis/practical/', ta_views.slide_practical_application, name='slide_practical_application'),  # Practical Application with TradingView
]
