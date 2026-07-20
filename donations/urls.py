from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_list, name='list'),
    path('<int:pk>/', views.donation_detail, name='detail'),
    path('<int:pk>/request/', views.request_donation, name='request'),
    path('my-requests/', views.my_requests, name='my_requests'),
]
