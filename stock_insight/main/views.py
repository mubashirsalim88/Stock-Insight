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
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from upstox_integration.models import Profile, Portfolio, CustomUser, Transaction
from django.contrib.auth import get_user_model
from upstox_integration.models import Profile, Portfolio, Transaction
from main.models import UserActivity
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from upstox_integration.models import Profile
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone



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
    profile = Profile.objects.get(user=request.user)
    
    # Assign default values if profile fields are None
    profile_data = {
        'phone_number': profile.phone_number if profile.phone_number else "Not provided",
        'gender': profile.gender if profile.gender else "Not provided",
        'profession': profile.profession if profile.profession else "Not provided",
        'trading_knowledge': profile.trading_knowledge if profile.trading_knowledge else "Not provided",
    }
    
    # Fetch the user's recent activities
    user_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]

    # Fetch user's portfolio (if any)
    portfolio = Portfolio.objects.filter(user=request.user)
    
    return render(request, 'home.html', {
        'profile': profile_data,
        'user_activities': user_activities,
        'portfolio': portfolio
    })

 

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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Check if the user is an admin
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to custom admin dashboard
            else:
                return redirect('home')  # Redirect non-admin users to the home page
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


@login_required
def admin_dashboard(request):
    User = get_user_model()
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(days=7)).count()  # Active users in the past week
    users_with_portfolio = Portfolio.objects.values('user').distinct().count()
    deleted_users_today = User.objects.filter(date_joined__gte=timezone.now().date()).count()  # You might need to adjust this based on your deletion tracking logic
    
    recent_user_activities = UserActivity.objects.order_by('-timestamp')[:5]
    recent_transactions = Transaction.objects.order_by('-date')[:5]
    recent_portfolio_changes = Portfolio.objects.order_by('-id')[:5]  # You may want to filter based on changes

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'users_with_portfolio': users_with_portfolio,
        'deleted_users_today': deleted_users_today,
        'recent_user_activities': recent_user_activities,
        'recent_transactions': recent_transactions,
        'recent_portfolio_changes': recent_portfolio_changes,
    }

    return render(request, 'admin_dashboard.html', context)


# Manage users view
@login_required
def manage_users(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Edit user view
@login_required
def edit_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Update user information
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        # You can add more fields to update here if needed

        user.save()
        messages.success(request, f"User {user.username} updated successfully!")
        return redirect('manage_users')

    return render(request, 'edit_user.html', {'user': user})

# Delete user view
@login_required
def delete_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User {user.username} deleted successfully!")
        return redirect('manage_users')

    return render(request, 'delete_user.html', {'user': user})



def logout(request):
    auth_logout(request)
    return redirect('index')
