# main/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from upstox_integration.models import Profile
from django.contrib.auth import logout as auth_logout
from .models import UserActivity
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def search_stock(request):
    if request.method == "GET":
        search_query = request.GET.get('q')  # Stock symbol entered by the user
        if search_query:
            # Log the search activity
            UserActivity.objects.create(
                user=request.user,
                action='search',
                stock_symbol=search_query
            )
            # Perform the actual search logic...
        return render(request, 'search_results.html', {'query': search_query})

@login_required
def view_stock(request, stock_symbol):
    # Log the view activity
    UserActivity.objects.create(
        user=request.user,
        action='view',
        stock_symbol=stock_symbol
    )
    
    # Fetch stock details and render the template
    return render(request, 'stock_detail.html', {'stock_symbol': stock_symbol})

@login_required
def home(request):
    # Fetch the user's profile
    profile = Profile.objects.get(user=request.user)  # Get the profile for the logged-in user
    return render(request, 'home.html', {'profile': profile})  # Pass the profile to the template

def index(request):
    return render(request, 'index.html')

def profile(request):
    return render(request, 'profile.html')

def premium_alerts(request):
    return render(request, 'premium_alerts.html')

def market_today(request):
    return render(request, 'market_today.html')

User = get_user_model()


@csrf_exempt
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        dob = request.POST.get('dob')  # Ensure this line retrieves the dob field
        gender = request.POST.get('gender')
        trading_knowledge = request.POST.get('trading_knowledge')
        profession = request.POST.get('profession')
        experience_level = request.POST.get('experience_level')
        interests = request.POST.get('interests')

        # Print the retrieved values for debugging
        print(f"Phone Number: {phone_number}, DOB: {dob}, Gender: {gender}, "
              f"Trading Knowledge: {trading_knowledge}, Profession: {profession}, "
              f"Experience: {experience_level}, Interests: {interests}")

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Username already taken. Please choose a different one.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use a different email.")
            return render(request, 'register.html')

        # Create the user
        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name
        )

        # Convert dob string to date format
        dob = datetime.strptime(dob, '%Y-%m-%d').date()  # Convert to date object

        # Check if the profile already exists and create or update it
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone_number = phone_number
        profile.dob = dob
        profile.gender = gender
        profile.trading_knowledge = trading_knowledge  # Ensure this field is set
        profile.profession = profession  # Save profession
        profile.experience = experience_level  # Save experience level
        profile.interests = interests  # Save interests
        profile.save()

        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')




@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']  # Authenticate using username instead of email
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Authenticate with username
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to the dashboard or home page
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('index')
