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

# def get_access_token():
#     try:
#         latest_token = UpstoxToken.objects.latest('created_at')
#         return latest_token.access_token
#     except UpstoxToken.DoesNotExist:
#         return None

# def get_real_time_price(symbol):
#     access_token = get_access_token()
#     if not access_token:
#         return None, "Missing or expired access token."

#     url = f"https://api-v2.upstox.com/v2/market-quote/ltp?symbol={symbol}"
#     headers = {'Authorization': f'Bearer {access_token}', 'accept': 'application/json'}

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         data = response.json()

#         if data.get('status') == 'success' and 'data' in data:
#             price_data_key = next(iter(data['data'].keys()))
#             price_data = data['data'].get(price_data_key)
#             if price_data and 'last_price' in price_data:
#                 return price_data['last_price'], None

#         return None, "Price data not found or empty."

#     except requests.exceptions.HTTPError as http_err:
#         return None, f"HTTP error occurred: {http_err}"
#     except requests.exceptions.RequestException as req_err:
#         return None, f"Request error: {req_err}"
#     except Exception as e:
#         return None, f"An unexpected error occurred: {str(e)}"

@login_required
def portfolio_overview(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    transactions = portfolio.transactions.all()
    return render(request, 'portfolio/overview.html', {
        'portfolio': portfolio,
        'transactions': transactions,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Portfolio, Transaction
from decimal import Decimal

@login_required
def buy_stock(request):
    if request.method == 'POST':
        stock_symbol = request.POST['symbol']
        shares = Decimal(request.POST['shares'])
        price_at_transaction = Decimal(request.POST['latestClose'])  # Use latestClose from frontend

        portfolio = get_object_or_404(Portfolio, user=request.user)
        Transaction.objects.create(
            portfolio=portfolio,
            stock_symbol=stock_symbol,
            transaction_type='BUY',
            shares=shares,
            price_at_transaction=price_at_transaction
        )

        portfolio.total_investment += (shares * price_at_transaction)
        portfolio.current_value += (shares * price_at_transaction)
        portfolio.save()

        return redirect('portfolio_overview')

    return redirect('real_time_charts')


@login_required
def sell_stock(request):
    if request.method == 'POST':
        stock_symbol = request.POST['symbol']
        shares = Decimal(request.POST['shares'])
        price_at_transaction = Decimal(request.POST['latestClose'])  # Use latestClose from frontend

        portfolio = get_object_or_404(Portfolio, user=request.user)
        total_shares_owned = portfolio.transactions.filter(
            stock_symbol=stock_symbol, transaction_type='BUY'
        ).aggregate(Sum('shares'))['shares__sum'] or 0

        if total_shares_owned >= shares:
            Transaction.objects.create(
                portfolio=portfolio,
                stock_symbol=stock_symbol,
                transaction_type='SELL',
                shares=shares,
                price_at_transaction=price_at_transaction
            )

            portfolio.total_investment -= (shares * price_at_transaction)
            portfolio.current_value -= (shares * price_at_transaction)
            portfolio.save()

            return redirect('portfolio_overview')
        else:
            return redirect('insufficient_shares_view')

    return redirect('real_time_charts')



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
