from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from donations.models import DonationListing
from accounts.models import CustomUser
from django.utils import timezone

def home(request):
    """Home page view."""
    # Calculate impact stats
    total_meals = DonationListing.objects.filter(
        status__in=['completed', 'picked_up']
    ).aggregate(total=Sum('quantity'))['total'] or 0

    active_donors = CustomUser.objects.filter(
        role='donor',
        donations__status__in=['available', 'pending', 'matched', 'claimed']
    ).distinct().count()

    verified_recipients = CustomUser.objects.filter(
        role='recipient',
        recipientprofile__is_verified=True
    ).count()

    cities_covered = DonationListing.objects.filter(
        status__in=['available', 'pending', 'matched', 'claimed']
    ).values('pickup_location').distinct().count()  # Simplified, in real app we'd have a city field

    # Get recent donations (last 6)
    recent_donations = DonationListing.objects.filter(
        status='available'
    ).select_related('donor').order_by('-created_at')[:6]

    context = {
        'meals_donated': total_meals,
        'active_donors': active_donors,
        'verified_recipients': verified_recipients,
        'cities_covered': cities_covered,
        'recent_donations': recent_donations,
    }
    return render(request, 'website/home.html', context)

def about(request):
    """About page view."""
    context = {}
    return render(request, 'website/about.html', context)

def contact(request):
    """Contact page view."""
    context = {}
    return render(request, 'website/contact.html', context)