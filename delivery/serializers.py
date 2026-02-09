from rest_framework import serializers
from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    donation_request = serializers.StringRelatedField()

    class Meta:
        model = Delivery
        fields = '__all__'
