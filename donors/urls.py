from django.urls import path
from . import views

app_name = 'donors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('donations/create/', views.create_donation, name='create_donation'),
    path('donations/<int:pk>/', views.donation_detail, name='donation_detail'),
    path('donations/', views.donation_list, name='donation_list'),
]