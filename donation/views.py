from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Donation

@login_required
def add_donation(request):
    if request.user.role != 'DONOR':
        return redirect('dashboard')

    if request.method == 'POST':
        Donation.objects.create(
            donor=request.user,
            food_name=request.POST['food_name'],
            quantity=request.POST['quantity'],
            pickup_address=request.POST['pickup_address'],
            expiry_date=request.POST['expiry_date'],
        )
        return redirect('donation:my_donations')

    return render(request, 'donation/add_donation.html')


@login_required
def my_donations(request):
    if request.user.role != 'DONOR':
        return redirect('dashboard')

    donations = Donation.objects.filter(donor=request.user)
    return render(request, 'donation/my_donations.html', {'donations': donations})


@login_required
def edit_donation(request, id):
    donation = get_object_or_404(Donation, id=id, donor=request.user)

    if request.method == 'POST':
        donation.food_name = request.POST['food_name']
        donation.quantity = request.POST['quantity']
        donation.pickup_address = request.POST['pickup_address']
        donation.expiry_date = request.POST['expiry_date']
        donation.save()
        return redirect('donation:my_donations')

    return render(request, 'donation/edit_donation.html', {'donation': donation})


@login_required
def delete_donation(request, id):
    donation = get_object_or_404(Donation, id=id, donor=request.user)
    donation.delete()
    return redirect('donation:my_donations')
