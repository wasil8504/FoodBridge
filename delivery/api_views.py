from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Delivery
from .serializers import DeliverySerializer

class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Delivery.objects.filter(
            donation_request__assigned_volunteer=self.request.user
        )
