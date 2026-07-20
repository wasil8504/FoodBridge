from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/recipient/', views.register_recipient, name='register_recipient'),
    path('profile/', views.profile, name='profile'),
]