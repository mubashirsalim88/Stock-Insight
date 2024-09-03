# main/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from upstox_integration.models import Profile
from django.contrib.auth import logout as auth_logout


def home(request):
    return render(request, 'home.html')

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
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        phone_number = request.POST['phone_number']
        dob = request.POST['dob']
        gender = request.POST['gender']

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

        # Create the profile only if it doesn't exist
        Profile.objects.get_or_create(user=user, defaults={
            'phone_number': phone_number,
            'dob': dob,
            'gender': gender
        })

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
    return redirect('home')

