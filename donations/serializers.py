from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DonationListing, MatchRequest, DonationImage
from donors.models import DonorProfile
from recipients.models import RecipientProfile, RecipientServiceArea

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone_number', 'address', 'email_verified',
                  'profile_completed', 'full_name']
        read_only_fields = ['id', 'email_verified', 'profile_completed']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class DonorProfileSerializer(serializers.ModelSerializer):
    """Serializer for DonorProfile model"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = DonorProfile
        fields = ['id', 'organization_name', 'donor_type', 'address',
                  'phone_number', 'email', 'license_number', 'is_verified',
                  'verification_date', 'verification_notes', 'total_donations',
                  'total_food_donated_kg', 'average_rating', 'user']


class RecipientProfileSerializer(serializers.ModelSerializer):
    """Serializer for RecipientProfile model"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = RecipientProfile
        fields = ['id', 'organization_name', 'recipient_type', 'address',
                  'phone_number', 'email', 'contact_person', 'registration_number',
                  'website', 'mission_description', 'food_preferences',
                  'food_restrictions', 'storage_capacity', 'has_refrigeration',
                  'has_storage', 'has_cooking_facilities', 'is_verified',
                  'verification_date', 'verification_notes', 'total_requests',
                  'total_meals_received', 'total_weight_received_kg',
                  'average_rating', 'success_rate', 'user']


class DonationImageSerializer(serializers.ModelSerializer):
    """Serializer for DonationImage model"""
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = DonationImage
        fields = ['id', 'image_url', 'caption', 'is_primary',
                  'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']


class DonationListingSerializer(serializers.ModelSerializer):
    """Serializer for DonationListing model"""
    donor = UserSerializer(read_only=True)
    donor_profile = DonorProfileSerializer(read_only=True)
    images = DonationImageSerializer(many=True, read_only=True)
    days_until_expiry = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_within_pickup_window = serializers.ReadOnlyField()
    is_available_for_claiming = serializers.ReadOnlyField()

    class Meta:
        model = DonationListing
        fields = [
            'id', 'food_type', 'description', 'quantity', 'quantity_unit',
            'status', 'pickup_location', 'pickup_window_start', 'pickup_window_end',
            'expiry_date', 'available_from', 'available_until',
            'special_handling_instructions', 'minimum_quantity', 'maximum_quantity',
            'photos', 'documentation_url', 'claimed_by', 'claimed_at',
            'estimated_meals', 'weight_kg', 'monetary_value_estimate',
            'created_at', 'updated_at', 'donor', 'donor_profile', 'images',
            'days_until_expiry', 'is_expired', 'is_within_pickup_window',
            'is_available_for_claiming'
        ]
        read_only_fields = [
            'id', 'donor', 'donor_profile', 'claimed_by', 'claimed_at',
            'estimated_meals', 'weight_kg', 'monetary_value_estimate',
            'created_at', 'updated_at', 'days_until_expiry', 'is_expired',
            'is_within_pickup_window', 'is_available_for_claiming'
        ]

    def validate(self, attrs):
        """Custom validation for donation data"""
        # Handle partial updates
        instance = getattr(self, 'instance', None)

        # Get values from attrs or instance
        pickup_window_start = attrs.get('pickup_window_start') or (getattr(instance, 'pickup_window_start', None) if instance else None)
        pickup_window_end = attrs.get('pickup_window_end') or (getattr(instance, 'pickup_window_end', None) if instance else None)
        expiry_date = attrs.get('expiry_date') or (getattr(instance, 'expiry_date', None) if instance else None)
        quantity = attrs.get('quantity') or (getattr(instance, 'quantity', None) if instance else None)
        minimum_quantity = attrs.get('minimum_quantity') or (getattr(instance, 'minimum_quantity', None) if instance else None)
        maximum_quantity = attrs.get('maximum_quantity') or (getattr(instance, 'maximum_quantity', None) if instance else None)
        available_from = attrs.get('available_from') or (getattr(instance, 'available_from', None) if instance else None)
        available_until = attrs.get('available_until') or (getattr(instance, 'available_until', None) if instance else None)

        # Validate timing
        if pickup_window_start and pickup_window_end:
            if pickup_window_start >= pickup_window_end:
                raise serializers.ValidationError({
                    'pickup_window_end': "Pickup window end must be after start time."
                })

        if expiry_date and pickup_window_end:
            if expiry_date < pickup_window_end:
                raise serializers.ValidationError({
                    'expiry_date': "Expiry date must be after pickup window end."
                })

        # Validate quantity constraints
        if minimum_quantity is not None and maximum_quantity is not None:
            if minimum_quantity > maximum_quantity:
                raise serializers.ValidationError({
                    'maximum_quantity': "Maximum quantity must be greater than minimum quantity."
                })
            if quantity is not None and quantity < minimum_quantity:
                raise serializers.ValidationError({
                    'quantity': f"Quantity must be at least {minimum_quantity} {attrs.get('quantity_unit', getattr(instance, 'quantity_unit', ''))}."
                })
            if quantity is not None and maximum_quantity is not None and quantity > maximum_quantity:
                raise serializers.ValidationError({
                    'quantity': f"Quantity cannot exceed {maximum_quantity} {attrs.get('quantity_unit', getattr(instance, 'quantity_unit', ''))}."
                })

        # Validate availability period
        if available_from and available_until:
            if available_until <= available_from:
                raise serializers.ValidationError({
                    'available_until': "Available until must be after available from."
                })

        return attrs


class MatchRequestSerializer(serializers.ModelSerializer):
    """Serializer for MatchRequest model"""
    donor = UserSerializer(source='donation.donor', read_only=True)
    recipient = UserSerializer(read_only=True)
    donation = DonationListingSerializer(read_only=True)
    recipient_profile = RecipientProfileSerializer(read_only=True)
    responded_by = UserSerializer(read_only=True)

    class Meta:
        model = MatchRequest
        fields = [
            'id', 'message', 'quantity_requested', 'quantity_unit',
            'preferred_pickup_time', 'special_instructions', 'status',
            'responded_at', 'responded_by', 'response_message',
            'requested_at', 'updated_at', 'donation', 'recipient',
            'recipient_profile', 'donor'
        ]
        read_only_fields = [
            'id', 'donation', 'recipient', 'responded_at',
            'responded_by', 'requested_at', 'updated_at'
        ]

    def validate(self, attrs):
        """Custom validation for match request"""
        # Handle partial updates
        instance = getattr(self, 'instance', None)

        # Get values from attrs or instance
        quantity_requested = attrs.get('quantity_requested') or (getattr(instance, 'quantity_requested', None) if instance else None)
        donation = attrs.get('donation') or (getattr(instance, 'donation', None) if instance else None)

        # Validate that requested quantity doesn't exceed donation limits
        if donation and quantity_requested is not None:
            if quantity_requested < donation.minimum_quantity:
                raise serializers.ValidationError({
                    'quantity_requested': f"Requested quantity must be at least {donation.minimum_quantity} {donation.quantity_unit}."
                })

            if donation.maximum_quantity and quantity_requested > donation.maximum_quantity:
                raise serializers.ValidationError({
                    'quantity_requested': f"Requested quantity cannot exceed {donation.maximum_quantity} {donation.quantity_unit}."
                })

        return attrs


# Simplified serializers for list views
class DonationListingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for donation lists"""
    donor = UserSerializer(read_only=True)
    days_until_expiry = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_within_pickup_window = serializers.ReadOnlyField()
    is_available_for_claiming = serializers.ReadOnlyField()

    class Meta:
        model = DonationListing
        fields = [
            'id', 'food_type', 'description', 'quantity', 'quantity_unit',
            'status', 'pickup_location', 'pickup_window_start', 'pickup_window_end',
            'expiry_date', 'available_from', 'available_until',
            'created_at', 'donor', 'days_until_expiry', 'is_expired',
            'is_within_pickup_window', 'is_available_for_claiming'
        ]


class MatchRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for match request lists"""
    donor = UserSerializer(source='donation.donor', read_only=True)
    recipient = UserSerializer(read_only=True)
    donation_food_type = serializers.CharField(source='donation.get_food_type_display', read_only=True)

    class Meta:
        model = MatchRequest
        fields = [
            'id', 'quantity_requested', 'quantity_unit', 'status',
            'requested_at', 'donation', 'donation_food_type',
            'recipient', 'donor'
        ]