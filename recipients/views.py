from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from donations.models import DonationListing, MatchRequest
from .models import RecipientProfile

@login_required
def dashboard(request):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    recipient_profile, _ = RecipientProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'organization_name': '',
            'recipient_type': 'other',
            'address': '',
            'phone_number': '',
            'email': request.user.email or '',
            'registration_number': '',
            'contact_person': request.user.username,
        },
    )

    requests = MatchRequest.objects.filter(recipient=request.user).order_by('-requested_at').select_related('donation', 'donation__donor')
    available_donations = DonationListing.objects.filter(status='available').order_by('-created_at')[:5]

    return render(request, 'recipients/dashboard.html', {
        'recipient_profile': recipient_profile,
        'requests': requests,
        'available_donations': available_donations,
    })

@login_required
def profile(request):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    recipient_profile, _ = RecipientProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'organization_name': '',
            'recipient_type': 'other',
            'address': '',
            'phone_number': '',
            'email': request.user.email or '',
            'registration_number': '',
            'contact_person': request.user.username,
        },
    )

    if request.method == 'POST':
        recipient_profile.organization_name = request.POST.get('organization_name', recipient_profile.organization_name)
        recipient_profile.recipient_type = request.POST.get('recipient_type', recipient_profile.recipient_type)
        recipient_profile.address = request.POST.get('address', recipient_profile.address)
        recipient_profile.phone_number = request.POST.get('phone_number', recipient_profile.phone_number)
        recipient_profile.email = request.POST.get('email', recipient_profile.email)
        recipient_profile.registration_number = request.POST.get('registration_number', recipient_profile.registration_number)
        recipient_profile.contact_person = request.POST.get('contact_person', recipient_profile.contact_person)
        recipient_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('recipients:profile')

    return render(request, 'recipients/profile.html', {'recipient_profile': recipient_profile})

@login_required
def donation_list(request):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    donations = DonationListing.objects.filter(status='available').order_by('-created_at')
    return render(request, 'recipients/donation_list.html', {'donations': donations})

@login_required
def donation_detail(request, pk):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    donation = get_object_or_404(DonationListing, pk=pk)
    return render(request, 'recipients/donation_detail.html', {'donation': donation})

@login_required
def request_donation(request, pk):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    donation = get_object_or_404(DonationListing, pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message', '')
        match_request, created = MatchRequest.objects.get_or_create(
            donation=donation,
            recipient=request.user,
            defaults={'message': message},
        )
        if created:
            donation.status = 'pending'
            donation.save(update_fields=['status'])
            messages.success(request, 'Donation request submitted successfully.')
        else:
            messages.info(request, 'You have already requested this donation.')
        return redirect('recipients:my_requests')

    return render(request, 'recipients/request_donation.html', {'donation': donation})

@login_required
def my_requests(request):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    requests = MatchRequest.objects.filter(recipient=request.user).order_by('-requested_at').select_related('donation', 'donation__donor')
    return render(request, 'recipients/my_requests.html', {'requests': requests})
