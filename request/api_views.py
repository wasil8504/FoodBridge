from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import DonationRequest
from .serializers import DonationRequestSerializer

class DonationRequestViewSet(ModelViewSet):
    serializer_class = DonationRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'NGO':
            return DonationRequest.objects.filter(ngo=user)
        if user.role == 'VOLUNTEER':
            return DonationRequest.objects.filter(assigned_volunteer=user)
        return DonationRequest.objects.none()
