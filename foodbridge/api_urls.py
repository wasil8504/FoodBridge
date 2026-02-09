from rest_framework.routers import DefaultRouter
from core.api_views import UserViewSet
from donation.api_views import DonationViewSet
from request.api_views import DonationRequestViewSet
from delivery.api_views import DeliveryViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('donations', DonationViewSet, basename='donations')
router.register('requests', DonationRequestViewSet, basename='requests')
router.register('deliveries', DeliveryViewSet, basename='deliveries')

urlpatterns = router.urls
