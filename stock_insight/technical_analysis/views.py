from django.shortcuts import render

# Landing Page
def landing_page(request):
    return render(request, 'technical_analysis/landing_page.html')

# Slide 1: Introduction to Stock Market
def slide_stock_market(request):
    return render(request, 'technical_analysis/slide_stock_market.html')

# Slide 2: Introduction to Trendlines
def slide_trendlines(request):
    return render(request, 'technical_analysis/slide_trendlines.html')

# Slide 3: Understanding Support and Resistance
def slide_support_resistance(request):
    return render(request, 'technical_analysis/slide_support_resistance.html')

# Slide 4: Introduction to Indicators (MACD, RSI)
def slide_indicators(request):
    return render(request, 'technical_analysis/slide_indicators.html')

# Slide 5: Candlestick Patterns
def slide_candlesticks(request):
    return render(request, 'technical_analysis/slide_candlesticks.html')

# Slide 6: Practical Application (TradingView Chart)
def slide_practical_application(request):
    return render(request, 'technical_analysis/slide_practical_application.html')
