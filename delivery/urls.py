from django.urls import path
from .views import *

app_name = 'delivery'

urlpatterns = [
    path('dashboard/', volunteer_dashboard, name='volunteer_dashboard'),
    path('start/<int:request_id>/', start_delivery, name='start_delivery'),
    path('complete/<int:delivery_id>/', complete_delivery, name='complete_delivery'),
]
