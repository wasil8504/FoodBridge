from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DonorProfile
from donations.models import DonationListing
from donations.forms import DonationListingForm

@login_required
def dashboard(request):
    """Donor dashboard view."""
    # Ensure the user is a donor
    if request.user.role != 'donor':
        messages.error(request, 'Access denied. Donor account required.')
        return redirect('website:home')

    # Get or create donor profile
    donor_profile, _ = DonorProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'organization_name': '',
            'donor_type': 'other',
            'address': '',
            'phone_number': '',
            'email': request.user.email or '',
            'license_number': '',
        },
    )

    # Get donor's donations
    donations = DonationListing.objects.filter(donor=request.user).order_by('-created_at')

    # Count donations by status
    stats = {
        'total': donations.count(),
        'available': donations.filter(status='available').count(),
        'pending': donations.filter(status='pending').count(),
        'completed': donations.filter(status__in=['completed', 'picked_up']).count(),
    }

    context = {
        'donor_profile': donor_profile,
        'donations': donations,
        'stats': stats,
    }
    return render(request, 'donors/dashboard.html', context)

@login_required
def profile(request):
    """Donor profile view."""
    if request.user.role != 'donor':
        messages.error(request, 'Access denied. Donor account required.')
        return redirect('website:home')

    donor_profile, _ = DonorProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'organization_name': '',
            'donor_type': 'other',
            'address': '',
            'phone_number': '',
            'email': request.user.email or '',
            'license_number': '',
        },
    )

    if request.method == 'POST':
        # Update profile
        donor_profile.organization_name = request.POST.get('organization_name', '')
        donor_profile.donor_type = request.POST.get('donor_type', '')
        donor_profile.address = request.POST.get('address', '')
        donor_profile.phone_number = request.POST.get('phone_number', '')
        donor_profile.license_number = request.POST.get('license_number', '')
        donor_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('donors:profile')

    context = {
        'donor_profile': donor_profile,
    }
    return render(request, 'donors/profile.html', context)

@login_required
def create_donation(request):
    """Create a new donation listing."""
    if request.user.role != 'donor':
        messages.error(request, 'Access denied. Donor account required.')
        return redirect('website:home')

    if request.method == 'POST':
        form = DonationListingForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            messages.success(request, 'Donation listing created successfully.')
            return redirect('donors:donation_detail', pk=donation.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DonationListingForm()

    context = {
        'form': form,
    }
    return render(request, 'donors/create_donation.html', context)

@login_required
def donation_detail(request, pk):
    """View donation details."""
    donation = get_object_or_404(DonationListing, pk=pk, donor=request.user)
    context = {
        'donation': donation,
    }
    return render(request, 'donors/donation_detail.html', context)

@login_required
def donation_list(request):
    """List all donations for the donor."""
    donations = DonationListing.objects.filter(donor=request.user).order_by('-created_at')
    context = {
        'donations': donations,
    }
    return render(request, 'donors/donation_list.html', context)