from django.urls import path
from . import views

app_name = 'recipients'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/<int:pk>/', views.donation_detail, name='donation_detail'),
    path('donations/<int:pk>/request/', views.request_donation, name='request_donation'),
    path('my-requests/', views.my_requests, name='my_requests'),
]