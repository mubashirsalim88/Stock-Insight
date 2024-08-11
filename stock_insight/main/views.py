from django.shortcuts import render

def home(request):
    return render(request,'home.html')

def profile(request):
    return render(request,'profile.html')

def real_time_charts(request):
    return render(request, 'real_time_charts.html')