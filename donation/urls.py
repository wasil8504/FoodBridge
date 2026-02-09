from django.urls import path
from .views import *

app_name = 'donation'

urlpatterns = [
    path('add/', add_donation, name='add_donation'),
    path('my/', my_donations, name='my_donations'),
    path('edit/<int:id>/', edit_donation, name='edit_donation'),
    path('delete/<int:id>/', delete_donation, name='delete_donation'),
]
