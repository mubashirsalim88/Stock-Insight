from django.shortcuts import redirect, render
from django.conf import settings
import urllib.parse
from django.http import HttpResponse, JsonResponse
import requests
from .models import UpstoxToken
from django.utils import timezone
from datetime import datetime, timedelta
from .instrument_keys import INSTRUMENT_KEYS
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone  # Import timezone for timestamps
from .models import Transaction, Portfolio

from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction, Portfolio
from django.conf import settings

@csrf_exempt  # If you're testing and want to skip CSRF checks; remove in production
def trade_stock(request):
    if request.method == 'POST':
        try:
            # Load JSON data from the request body
            data = json.loads(request.body)
            stock_symbol = data.get('symbol')
            shares = Decimal(data.get('shares', 0))
            action = data.get('action')
            price = Decimal(data.get('price'))

            print(f"Received data: {data}")  # Log all received data
            print(f"Received price: {price}")  # Log the price received

            # Validation checks
            if stock_symbol is None or action is None:
                return JsonResponse({'error': 'Symbol and action are required.'}, status=400)

            if action not in ['buy', 'sell']:
                return JsonResponse({'error': 'Action must be buy or sell.'}, status=400)

            if shares <= 0 or price <= 0:
                return JsonResponse({'error': 'Shares and price must be positive values.'}, status=400)

            # Create a new transaction
            Transaction.objects.create(
                user=request.user,
                stock_symbol=stock_symbol,
                shares=int(shares),  # Convert shares to an integer
                action=action,
                price=price
            )

            # Update portfolio based on action
            portfolio, created = Portfolio.objects.get_or_create(
                user=request.user,
                stock_symbol=stock_symbol,
                defaults={'shares': 0, 'average_price': Decimal(0)}
            )

            if action == 'buy':
                # Calculate new average price
                total_cost = (portfolio.average_price * Decimal(portfolio.shares)) + (price * shares)
                portfolio.shares += int(shares)
                portfolio.average_price = total_cost / Decimal(portfolio.shares)
                portfolio.save()
                message = f"Successfully bought {int(shares)} shares of {stock_symbol}."

            elif action == 'sell':
                if portfolio.shares < shares:
                    return JsonResponse({'error': 'Insufficient shares to sell'}, status=400)
                portfolio.shares -= int(shares)
                if portfolio.shares == 0:
                    portfolio.average_price = Decimal(0)  # Reset average price if no shares are left
                else:
                    # Update average price when shares remain
                    total_cost = (portfolio.average_price * Decimal(portfolio.shares)) + (price * shares)
                    portfolio.average_price = total_cost / Decimal(portfolio.shares)
                portfolio.save()
                message = f"Successfully sold {int(shares)} shares of {stock_symbol}."

            return JsonResponse({'message': message})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")  # Log the error for debugging
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




from django.shortcuts import render
from .models import Portfolio, Transaction
from django.db.models import Sum, F

def view_portfolio(request):
    portfolio = Portfolio.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')  # Assuming 'date' is your date field in the Transaction model

    # Calculate total shares and total investment value
    total_shares = portfolio.aggregate(Sum('shares'))['shares__sum'] or 0
    total_investment_value = sum(item.average_price * item.shares for item in portfolio)

    context = {
        'portfolio': portfolio,
        'transactions': transactions,
        'total_shares': total_shares,
        'total_investment_value': total_investment_value
    }
    return render(request, 'portfolio.html', context)



def fetch_historical_data(request, stock_symbol):
    try:
        timeframe = request.GET.get('timeframe', 'day')
        instrument_key = INSTRUMENT_KEYS.get(stock_symbol)

        if not instrument_key:
            return JsonResponse({'error': 'Invalid stock symbol.'}, status=400)

        latest_token = UpstoxToken.objects.latest('created_at')
        access_token = latest_token.access_token

        end_date = datetime.now().strftime('%Y-%m-%d')

        if timeframe == 'day':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        else:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        url = f"https://api-v2.upstox.com/v2/historical-candle/{instrument_key}/{timeframe}/{end_date}/{start_date}"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'accept': 'application/json',
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return JsonResponse({timeframe: response.json()})
        else:
            return JsonResponse({'error': f"Upstox API error: {response.text}"}, status=response.status_code)

    except UpstoxToken.DoesNotExist:
        return JsonResponse({'error': 'No access token found.'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def real_time_charts(request):
    try:
        latest_token = UpstoxToken.objects.latest('created_at')
        access_token = latest_token.access_token
    except UpstoxToken.DoesNotExist:
        access_token = None

    return render(request, 'real_time_charts.html', {'access_token': access_token})

def upstox_authorize(request):
    client_id = settings.UPSTOX_API_KEY
    redirect_uri = settings.UPSTOX_REDIRECT_URI
    state = 'optional_state'
    upstox_auth_url = "https://api-v2.upstox.com/v2/login/authorization/dialog"
    query_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
    }
    url = f"{upstox_auth_url}?{urllib.parse.urlencode(query_params)}"
    return redirect(url)

def upstox_callback(request):
    # Log the request parameters for debugging
    print("Request GET parameters:", request.GET)
    
    authorization_code = request.GET.get('code')
    if authorization_code:
        url = "https://api-v2.upstox.com/v2/login/authorization/token"
        data = {
            'code': authorization_code,
            'client_id': settings.UPSTOX_API_KEY,
            'client_secret': settings.UPSTOX_API_SECRET,
            'redirect_uri': settings.UPSTOX_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        response = requests.post(url, data=data)
        access_token_info = response.json()
        print("Upstox response:", access_token_info)  # Log response content

        if response.status_code == 200 and 'access_token' in access_token_info:
            access_token = access_token_info.get('access_token')
            expires_in = access_token_info.get('expires_in', 0)
            token_type = access_token_info.get('token_type', 'N/A')

            UpstoxToken.objects.create(
                access_token=access_token,
                expires_in=expires_in,
                token_type=token_type,
                created_at=timezone.now()
            )
            return HttpResponse("Authorization successful and token saved.")
        else:
            error_message = access_token_info.get('error_description', 'Unknown error')
            return HttpResponse(f"Error during token exchange: {error_message}")
    else:
        return HttpResponse("Authorization failed: No authorization code provided.")

    


import os
import pickle
import yfinance as yf
import pandas as pd
from django.shortcuts import render
from django.conf import settings

# Load the pre-trained model from the file
def load_model():
    # Get the correct path to the model using BASE_DIR
    model_path = os.path.join(settings.BASE_DIR, 'stock_insight', 'ml_models', 'stock_recommendation_model.pkl')
    
    # Check if the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    
    return model

# Function to fetch stock data using yfinance
def get_stock_data(stock):
    ticker = yf.Ticker(stock)
    info = ticker.info

    # Extract relevant features
    eps = info.get("trailingEps", None)
    pe_ratio = info.get("trailingPE", None)
    dividend_yield = info.get("dividendYield", None)
    pb_ratio = info.get("priceToBook", None)
    debt_equity_ratio = info.get("debtToEquity", None)
    
    print(f"Fetching data for {stock}:")
    print(f"EPS: {eps}, PE Ratio: {pe_ratio}, Dividend Yield: {dividend_yield}, P/B Ratio: {pb_ratio}, Debt/Equity Ratio: {debt_equity_ratio}")
    
    return {
        "Stock": stock,
        "EPS": eps,
        "P/E Ratio": pe_ratio,
        "Dividend Yield": dividend_yield,
        "P/B Ratio": pb_ratio,
        "Debt/Equity Ratio": debt_equity_ratio
    }

# Function to classify stocks based on investment horizon
def classify_stock(row, horizon):
    if horizon == 'Short-term':
        if row['Debt/Equity Ratio'] < 0.5 and row['P/E Ratio'] < 15:
            return 'Buy'
        elif row['Debt/Equity Ratio'] > 1.0 or row['P/E Ratio'] > 30:
            return 'Sell'
        else:
            return 'Hold'
    elif horizon == 'Medium-term':
        if 10 <= row['P/E Ratio'] <= 25 and row['EPS'] > 5:
            return 'Buy'
        elif row['P/E Ratio'] > 30 or row['EPS'] < 1:
            return 'Sell'
        else:
            return 'Hold'
    elif horizon == 'Long-term':
        if row['Dividend Yield'] > 0.02 and row['EPS'] > 5:
            return 'Buy'
        elif row['Dividend Yield'] is None or row['EPS'] < 2:
            return 'Sell'
        else:
            return 'Hold'
    return 'Hold'

# Function to handle the stock recommendation view
def recommendations(request):
    recommendations = None
    horizon = None
    stocks = ["HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", 
              "MARUTI.NS", "LT.NS", "AXISBANK.NS", "SUNPHARMA.NS", "WIPRO.NS", "BAJFINANCE.NS", 
              "M&M.NS", "HCLTECH.NS", "ULTRACEMCO.NS", "TECHM.NS", "TITAN.NS", "HEROMOTOCO.NS", 
              "DRREDDY.NS", "POWERGRID.NS", "TATAMOTORS.NS", "NTPC.NS", "ONGC.NS"]

    if request.method == "POST":
        horizon = request.POST.get('horizon')

        # Fetch stock data
        data = [get_stock_data(stock) for stock in stocks]
        df = pd.DataFrame(data)
        df = df.dropna()  # Remove rows with missing data

        # Load the model
        model = load_model()

        # Define the features for prediction
        X = df[['EPS', 'P/E Ratio', 'Dividend Yield', 'P/B Ratio', 'Debt/Equity Ratio']]
        
        # Mock labels for the sake of classification
        y = [classify_stock(row, horizon) for _, row in df.iterrows()]

        # Apply recommendations
        df['Recommendation'] = y

        # Convert recommendations to a dictionary for rendering
        recommendations = df[['Stock', 'EPS', 'P/E Ratio', 'Dividend Yield', 'P/B Ratio', 'Debt/Equity Ratio', 'Recommendation']].to_dict('records')

    return render(request, 'stock_recommendation.html', {
        'recommendations': recommendations,
        'horizon': horizon,
    })
