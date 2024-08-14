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
        url = f"https://api-v2.upstox.com/v2/historical-candle/{instrument_key}/30minute/{end_date}/{start_date}"

        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'accept': 'application/json',
        }

        # Make the request to the Upstox API
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return JsonResponse(response.json())  # Return the JSON response
        else:
            return JsonResponse({'error': f'Upstox API error: {response.text}'}, status=response.status_code)

    except UpstoxToken.DoesNotExist:
        return JsonResponse({'error': 'No access token found.'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def real_time_charts(request):
    return render(request, 'real_time_charts.html')


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