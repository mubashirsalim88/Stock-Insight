from django.shortcuts import redirect
from django.conf import settings
import urllib.parse
from django.http import HttpResponse
import requests
from django.shortcuts import render
from .models import UpstoxToken
from django.utils import timezone
from django.http import JsonResponse
from .instrument_keys import INSTRUMENT_KEYS 
from datetime import datetime, timedelta



def fetch_historical_data(request, stock_symbol):
    try:
        # Fetch the instrument key based on the provided stock symbol
        instrument_key = INSTRUMENT_KEYS.get(stock_symbol)

        if not instrument_key:
            return JsonResponse({'error': 'Invalid stock symbol.'}, status=400)

        # Fetch the latest access token from the database
        latest_token = UpstoxToken.objects.latest('created_at')
        access_token = latest_token.access_token

        # Calculate date range dynamically
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        # URLs for 30-minute and daily data
        url_30min = f"https://api-v2.upstox.com/v2/historical-candle/{instrument_key}/30minute/{end_date}/{start_date}"
        url_day = f"https://api-v2.upstox.com/v2/historical-candle/{instrument_key}/day/{end_date}/{start_date}"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'accept': 'application/json',
        }

        # Make the request to the Upstox API for 30-minute data
        response_30min = requests.get(url_30min, headers=headers)
        # Make the request to the Upstox API for daily data
        response_day = requests.get(url_day, headers=headers)

        # Check if both requests were successful
        if response_30min.status_code == 200 and response_day.status_code == 200:
            return JsonResponse({
                '30minute': response_30min.json(),
                'day': response_day.json()
            })
        else:
            error_message = f"Upstox API error: {response_30min.text if response_30min.status_code != 200 else response_day.text}"
            return JsonResponse({'error': error_message}, status=response_30min.status_code if response_30min.status_code != 200 else response_day.status_code)

    except UpstoxToken.DoesNotExist:
        return JsonResponse({'error': 'No access token found.'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





def real_time_charts(request):
    # Fetch the latest access token
    try:
        latest_token = UpstoxToken.objects.latest('created_at')
        access_token = latest_token.access_token
    except UpstoxToken.DoesNotExist:
        access_token = None

    return render(request, 'real_time_charts.html', {
        'access_token': access_token
    })



def upstox_authorize(request):
    client_id = settings.UPSTOX_API_KEY
    redirect_uri = settings.UPSTOX_REDIRECT_URI
    state = 'optional_state'
    upstox_auth_url = "https://api.upstox.com/v2/login/authorization/dialog"
    query_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
    }
    url = f"{upstox_auth_url}?{urllib.parse.urlencode(query_params)}"
    return redirect(url)

def upstox_callback(request):
    authorization_code = request.GET.get('code')
    if authorization_code:
        url = "https://api.upstox.com/v2/login/authorization/token"
        data = {
            'code': authorization_code,
            'client_id': settings.UPSTOX_API_KEY,
            'client_secret': settings.UPSTOX_API_SECRET,
            'redirect_uri': settings.UPSTOX_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        response = requests.post(url, data=data)
        response_content = response.content.decode('utf-8')
        access_token_info = response.json()

        # Log the full response for debugging
        print(f"Response Content: {response_content}")

        if response.status_code == 200 and 'access_token' in access_token_info:
            # Extract fields with default values if keys are missing
            access_token = access_token_info.get('access_token')
            expires_in = access_token_info.get('expires_in', None)  # Default to None if not provided
            token_type = access_token_info.get('token_type', None)

            # Save the token in the database
            UpstoxToken.objects.create(
                access_token=access_token,
                expires_in=expires_in if expires_in is not None else 0,  # Store 0 if not provided
                token_type=token_type if token_type is not None else "N/A",  # Store "N/A" if not provided
                created_at=timezone.now()
            )
            return HttpResponse("Authorization successful and token saved.")
        else:
            # Log the error details and display a user-friendly message
            error_message = access_token_info.get('error_description', 'Unknown error')
            return HttpResponse(f"Error during token exchange: {error_message}<br>Full response: {response_content}")
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
def stock_recommendation_view(request):
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
