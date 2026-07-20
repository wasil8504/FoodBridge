from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DonationListing, MatchRequest


def donation_list(request):
    donations = DonationListing.objects.filter(status='available').order_by('-created_at')
    return render(request, 'donations/donation_list.html', {'donations': donations})


def donation_detail(request, pk):
    donation = get_object_or_404(DonationListing, pk=pk)
    return render(request, 'donations/donation_detail.html', {'donation': donation})

@login_required
def request_donation(request, pk):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    donation = get_object_or_404(DonationListing, pk=pk)
    match_request, created = MatchRequest.objects.get_or_create(
        donation=donation,
        recipient=request.user,
        defaults={'message': request.POST.get('message', '') if request.method == 'POST' else ''},
    )

    if request.method == 'POST':
        if created:
            donation.status = 'pending'
            donation.save(update_fields=['status'])
            messages.success(request, 'Donation request submitted successfully.')
        else:
            messages.info(request, 'You have already requested this donation.')
        return redirect('donations:my_requests')

    return render(request, 'donations/request_donation.html', {'donation': donation, 'match_request': match_request})

@login_required
def my_requests(request):
    if request.user.role != 'recipient':
        messages.error(request, 'Access denied. Recipient account required.')
        return redirect('website:home')

    requests = MatchRequest.objects.filter(recipient=request.user).order_by('-requested_at').select_related('donation', 'donation__donor')
    return render(request, 'donations/my_requests.html', {'requests': requests})
