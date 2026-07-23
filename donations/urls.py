from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'donations'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'donations', views.DonationListingViewSet, basename='donation')
router.register(r'requests', views.MatchRequestViewSet, basename='request')
router.register(r'images', views.DonationImageViewSet, basename='donation-image')

urlpatterns = [
    path('api/', include(router.urls)),
]