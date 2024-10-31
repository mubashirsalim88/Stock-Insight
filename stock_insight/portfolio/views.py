from django.shortcuts import render, redirect
from .models import Portfolio, Transaction, StockData
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages


@login_required
def portfolio_overview(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    transactions = portfolio.transactions.all()
    return render(request, 'portfolio/overview.html', {
        'portfolio': portfolio,
        'transactions': transactions,
    })


@login_required
def buy_stock(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        shares = int(request.POST.get('shares'))

        try:
            # Try to fetch price from StockData
            stock = StockData.objects.get(stock_symbol__iexact=symbol)  # Case-insensitive match
            price = stock.last_price
        except StockData.DoesNotExist:
            # Show error message if symbol not found
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Buy Stock',
                'button_text': 'Buy',
                'error_message': f"Stock symbol '{symbol}' not found.",
            })

        # Create or update portfolio
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        Transaction.objects.create(
            portfolio=portfolio,
            stock_symbol=symbol,
            transaction_type='BUY',
            shares=shares,
            price_at_transaction=price,
            date=timezone.now(),
        )

        # Update portfolio value
        portfolio.total_investment += price * shares
        portfolio.current_value += price * shares
        portfolio.save()

        return redirect('portfolio_overview')

    return render(request, 'portfolio/buysellform.html', {
        'form_title': 'Buy Stock',
        'button_text': 'Buy',
    })

@login_required
def sell_stock(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        shares = int(request.POST.get('shares'))

        try:
            # Fetch price from StockData
            stock = StockData.objects.get(stock_symbol__iexact=symbol)
            price = stock.last_price
        except StockData.DoesNotExist:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Sell Stock',
                'button_text': 'Sell',
                'error_message': f"Stock symbol '{symbol}' not found.",
            })

        # Retrieve or create portfolio
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        
        # Check if enough shares are available to sell
        total_shares = Transaction.objects.filter(
            portfolio=portfolio, stock_symbol=symbol, transaction_type='BUY'
        ).aggregate(Sum('shares'))['shares__sum'] or 0
        total_shares -= Transaction.objects.filter(
            portfolio=portfolio, stock_symbol=symbol, transaction_type='SELL'
        ).aggregate(Sum('shares'))['shares__sum'] or 0

        if total_shares >= shares:
            Transaction.objects.create(
                portfolio=portfolio,
                stock_symbol=symbol,
                transaction_type='SELL',
                shares=shares,
                price_at_transaction=price,
                date=timezone.now(),
            )

            portfolio.current_value -= price * shares
            portfolio.save()
            return redirect('portfolio_overview')
        else:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Sell Stock',
                'button_text': 'Sell',
                'error_message': 'Insufficient shares to sell.',
            })

    return render(request, 'portfolio/buysellform.html', {
        'form_title': 'Sell Stock',
        'button_text': 'Sell',
    })


@login_required
def portfolio_performance(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    transactions = portfolio.transactions.all().order_by('transaction_date')

    # Accumulate daily portfolio values
    performance_data = []
    current_value = 0
    for transaction in transactions:
        if transaction.transaction_type == 'BUY':
            current_value += transaction.shares * transaction.price_at_transaction
        elif transaction.transaction_type == 'SELL':
            current_value -= transaction.shares * transaction.price_at_transaction
        performance_data.append({
            'date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'value': current_value,
        })

    return JsonResponse(performance_data, safe=False)
