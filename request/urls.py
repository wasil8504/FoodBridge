from django.urls import path
from .views import *

app_name = 'request_donation'

urlpatterns = [
    path('dashboard/', ngo_dashboard, name='ngo_dashboard'),
    path('available/', available_donations, name='available_donations'),
    path('request/<int:donation_id>/', request_donation, name='request_donation'),
    path('assign/<int:request_id>/', assign_volunteer, name='assign_volunteer'),
]
