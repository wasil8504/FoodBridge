from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Donation
from .serializers import DonationSerializer

class DonationViewSet(ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'DONOR':
            return Donation.objects.filter(donor=self.request.user)
        return Donation.objects.all()

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)
