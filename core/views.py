from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User

def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password'],
            role=request.POST['role']
        )
        login(request, user)
        return redirect('dashboard')
    return render(request, 'core/register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.role == 'DONOR':
        return redirect('donation:my_donations')
    elif request.user.role == 'NGO':
        return redirect('request_donation:ngo_dashboard')
    else:
        return redirect('delivery:volunteer_dashboard')
