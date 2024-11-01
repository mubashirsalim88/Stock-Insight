from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from .models import Portfolio, Transaction
from upstox_integration.models import UpstoxToken
from upstox_integration.instrument_keys import INSTRUMENT_KEYS
from decimal import Decimal
import requests

def get_access_token():
    try:
        latest_token = UpstoxToken.objects.latest('created_at')
        return latest_token.access_token
    except UpstoxToken.DoesNotExist:
        return None


def get_real_time_price(symbol):
    """
    Fetch real-time price for a single symbol using the instrument key.
    :param symbol: A stock symbol in the required format (e.g., "NSE_EQ|INE009A01021")
    :return: The price of the symbol, or an error message if fetching fails.
    """
    access_token = get_access_token()
    
    if not access_token:
        return None, "Missing or expired access token."
    
    url = f"https://api-v2.upstox.com/v2/market-quote/ltp?symbol={symbol}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': 'application/json',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Log the raw JSON response for debugging purposes
        data = response.json()
        print("API response data:", data)

        # Check if the API call was successful and price data is present
        if data.get('status') == 'success' and 'data' in data:
            # Get the exact key from data['data'] to handle symbol format variations
            price_data_key = next(iter(data['data'].keys()))
            price_data = data['data'].get(price_data_key)
            if price_data and 'last_price' in price_data:
                return price_data['last_price'], None
            
        return None, "Price data not found or empty."

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None, f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None, f"Request error: {req_err}"
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None, f"An unexpected error occurred: {str(e)}"



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
        
        # Get the instrument key from the INSTRUMENT_KEYS dict
        instrument_key = INSTRUMENT_KEYS.get(symbol)
        if not instrument_key:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Buy Stock',
                'button_text': 'Buy',
                'error_message': 'Invalid stock symbol.',
            })
        
        price, error_message = get_real_time_price(instrument_key)
        
        if error_message:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Buy Stock',
                'button_text': 'Buy',
                'error_message': error_message,
            })

        if price is None or not isinstance(price, (int, float)):
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Buy Stock',
                'button_text': 'Buy',
                'error_message': 'Invalid price received.',
            })

        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        Transaction.objects.create(
            portfolio=portfolio,
            stock_symbol=symbol,
            transaction_type='BUY',
            shares=shares,
            price_at_transaction=price,
            transaction_date=timezone.now(),
        )
        
        portfolio.total_investment += Decimal(price) * shares
        portfolio.current_value += Decimal(price) * shares
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
        
        # Get the instrument key from the INSTRUMENT_KEYS dict
        instrument_key = INSTRUMENT_KEYS.get(symbol)
        if not instrument_key:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Sell Stock',
                'button_text': 'Sell',
                'error_message': 'Invalid stock symbol.',
            })

        price, error_message = get_real_time_price(instrument_key)

        if error_message:
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Sell Stock',
                'button_text': 'Sell',
                'error_message': error_message,
            })

        if price is None or not isinstance(price, (int, float)):
            return render(request, 'portfolio/buysellform.html', {
                'form_title': 'Sell Stock',
                'button_text': 'Sell',
                'error_message': 'Invalid price received.',
            })

        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

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
                transaction_date=timezone.now(),
            )

            portfolio.current_value -= Decimal(price) * shares
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
def portfolio_real_time_value(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    transactions = portfolio.transactions.filter(transaction_type='BUY')
    total_current_value = 0

    for transaction in transactions:
        symbol = transaction.stock_symbol
        instrument_key = INSTRUMENT_KEYS.get(symbol)
        if not instrument_key:
            continue
        price, error_message = get_real_time_price(instrument_key)
        if error_message:
            continue
        if price is not None:
            total_current_value += price * transaction.shares

    return JsonResponse({
        'current_value': total_current_value,
        'total_investment': portfolio.total_investment
    })


@login_required
def portfolio_performance(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    transactions = portfolio.transactions.all().order_by('transaction_date')

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
