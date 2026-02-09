from rest_framework import serializers
from .models import DonationRequest

class DonationRequestSerializer(serializers.ModelSerializer):
    donation = serializers.StringRelatedField()
    ngo = serializers.StringRelatedField()
    assigned_volunteer = serializers.StringRelatedField()

    class Meta:
        model = DonationRequest
        fields = '__all__'
