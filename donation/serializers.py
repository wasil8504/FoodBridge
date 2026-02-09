from rest_framework import serializers
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.StringRelatedField()

    class Meta:
        model = Donation
        fields = '__all__'
