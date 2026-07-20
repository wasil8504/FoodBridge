from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import DonorSignUpForm, RecipientSignUpForm, CustomLoginForm

def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate by username or email
            user = authenticate(request, username=username, password=password)
            if user is None:
                from .models import CustomUser
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                # Redirect based on role
                if user.role == 'donor':
                    return redirect('donors:dashboard')
                elif user.role == 'recipient':
                    return redirect('recipients:dashboard')
                elif user.role == 'admin':
                    return redirect('admin:index')
                else:
                    return redirect('website:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('website:home')

def register_donor(request):
    if request.method == 'POST':
        form = DonorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Please complete your profile.')
            return redirect('donors:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DonorSignUpForm()
    return render(request, 'accounts/register_donor.html', {'form': form})

def register_recipient(request):
    if request.method == 'POST':
        form = RecipientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Please complete your profile.')
            return redirect('recipients:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipientSignUpForm()
    return render(request, 'accounts/register_recipient.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')