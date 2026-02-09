from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from donation.models import Donation
from core.models import User
from .models import DonationRequest

@login_required
def ngo_dashboard(request):
    if request.user.role != 'NGO':
        return redirect('dashboard')

    requests = DonationRequest.objects.filter(ngo=request.user)
    return render(request, 'request/ngo_dashboard.html', {'requests': requests})


@login_required
def available_donations(request):
    if request.user.role != 'NGO':
        return redirect('dashboard')

    donations = Donation.objects.filter(is_requested=False)
    return render(request, 'request/available_donations.html', {'donations': donations})


@login_required
def request_donation(request, donation_id):
    if request.user.role != 'NGO':
        return redirect('dashboard')

    donation = get_object_or_404(Donation, id=donation_id)

    DonationRequest.objects.create(
        donation=donation,
        ngo=request.user
    )

    donation.is_requested = True
    donation.save()

    return redirect('request_donation:ngo_dashboard')


@login_required
def assign_volunteer(request, request_id):
    if request.user.role != 'NGO':
        return redirect('dashboard')

    donation_request = get_object_or_404(DonationRequest, id=request_id)
    volunteers = User.objects.filter(role='VOLUNTEER')

    if request.method == 'POST':
        volunteer_id = request.POST['volunteer']
        donation_request.assigned_volunteer_id = volunteer_id
        donation_request.status = 'ASSIGNED'
        donation_request.save()
        return redirect('request_donation:ngo_dashboard')

    return render(
        request,
        'request/assign_volunteer.html',
        {
            'donation_request': donation_request,
            'volunteers': volunteers
        }
    )
