from django.shortcuts import render

# Landing Page
def landing_page(request):
    return render(request, 'technical_analysis/landing_page.html')

# Slide 1: Introduction to Stock Market
def slide_stock_market(request):
    return render(request, 'technical_analysis/slide_stock_market.html')

# Slide 2: Other Markets (Forex, Crypto, etc.)
def slide_other_markets(request):
    return render(request, 'technical_analysis/slide_other_markets.html')

# Slide 3: Trading vs Investing - Types of Traders
def slide_trading_vs_investing(request):
    return render(request, 'technical_analysis/slide_trading_vs_investing.html')

# Slide 4: Technical Analysis - Charts (Line Graph, Candlestick Chart)
def slide_technical_analysis_charts(request):
    return render(request, 'technical_analysis/slide_technical_analysis_charts.html')

# Slide 5: Price Action
def slide_price_action(request):
    return render(request, 'technical_analysis/slide_price_action.html')

# Slide 6: Understanding Support and Resistance
def slide_support_resistance(request):
    return render(request, 'technical_analysis/slide_support_resistance.html')

# Slide 7: Introduction to Trendlines
def slide_trendlines(request):
    return render(request, 'technical_analysis/slide_trendlines.html')

# Slide 8: Other Price Action Techniques
def slide_other_price_action(request):
    return render(request, 'technical_analysis/slide_other_price_action.html')

# Slide 9: Introduction to Indicators (MACD, RSI)
def slide_indicators(request):
    return render(request, 'technical_analysis/slide_indicators.html')

# Slide 10: Candlestick Patterns
def slide_candlesticks(request):
    return render(request, 'technical_analysis/slide_candlesticks.html')

# Slide 11: Practical Application (TradingView Chart)
def slide_practical_application(request):
    return render(request, 'technical_analysis/slide_practical_application.html')
