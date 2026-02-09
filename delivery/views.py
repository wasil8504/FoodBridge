from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from request.models import DonationRequest
from .models import Delivery

@login_required
def volunteer_dashboard(request):
    if request.user.role != 'VOLUNTEER':
        return redirect('dashboard')

    requests = DonationRequest.objects.filter(
        assigned_volunteer=request.user
    )

    return render(
        request,
        'delivery/volunteer_dashboard.html',
        {'requests': requests}
    )


@login_required
def start_delivery(request, request_id):
    if request.user.role != 'VOLUNTEER':
        return redirect('dashboard')

    donation_request = get_object_or_404(
        DonationRequest,
        id=request_id,
        assigned_volunteer=request.user
    )

    Delivery.objects.get_or_create(
        donation_request=donation_request
    )

    return redirect('delivery:volunteer_dashboard')


@login_required
def complete_delivery(request, delivery_id):
    if request.user.role != 'VOLUNTEER':
        return redirect('dashboard')

    delivery = get_object_or_404(
        Delivery,
        id=delivery_id,
        donation_request__assigned_volunteer=request.user
    )

    delivery.status = 'COMPLETED'
    delivery.save()

    return redirect('delivery:volunteer_dashboard')
