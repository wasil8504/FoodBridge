from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
import json


class DonationListing(models.Model):
    FOOD_TYPE_CHOICES = [
        ('prepared_meals', 'Prepared Meals'),
        ('fresh_produce', 'Fresh Produce'),
        ('bakery', 'Bakery Items'),
        ('dairy', 'Dairy Products'),
        ('meat_poultry', 'Meat & Poultry'),
        ('canned_goods', 'Canned Goods'),
        ('dry_goods', 'Dry Goods'),
        ('frozen', 'Frozen Foods'),
        ('beverages', 'Beverages'),
        ('other', 'Other'),
    ]

    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('grams', 'Grams'),
        ('lbs', 'Pounds'),
        ('ounces', 'Ounces'),
        ('liters', 'Liters'),
        ('milliliters', 'Milliliters'),
        ('pieces', 'Pieces'),
        ('portions', 'Portions'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags'),
        ('containers', 'Containers'),
        ('pallets', 'Pallets'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Match'),
        ('matched', 'Matched'),
        ('claimed', 'Claimed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    # Core relationships
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donations',
        help_text="User who created this donation"
    )
    donor_profile = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations',
        help_text="Donor profile (for performance optimization)"
    )

    # Food details
    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE_CHOICES,
        help_text="Type of food being donated"
    )
    description = models.TextField(
        help_text="Detailed description of the food items"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        help_text="Quantity of food available"
    )
    quantity_unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='kg',
        help_text="Unit of measurement for quantity"
    )

    # Timing and availability
    expiry_date = models.DateTimeField(
        help_text="Date and time when the food expires and becomes unsafe"
    )
    pickup_location = models.TextField(
        help_text="Specific location where food can be picked up"
    )
    pickup_window_start = models.DateTimeField(
        help_text="Earliest time when food can be picked up"
    )
    pickup_window_end = models.DateTimeField(
        help_text="Latest time when food can be picked up"
    )
    available_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this donation listing becomes available"
    )
    available_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this donation listing expires (if different from food expiry)"
    )

    # Logistics
    special_handling_instructions = models.TextField(
        blank=True,
        help_text="Special instructions for handling (e.g., keep refrigerated, fragile)"
    )
    minimum_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.001,
        validators=[MinValueValidator(0.001)],
        help_text="Minimum quantity that can be claimed at once"
    )
    maximum_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        help_text="Maximum quantity that can be claimed at once (null for no limit)",
        blank=True,
        null=True
    )

    # Media and documentation
    photos = models.JSONField(
        default=list,
        blank=True,
        help_text="List of photo URLs showing the food items"
    )
    documentation_url = models.URLField(
        blank=True,
        help_text="URL to additional documentation (certificates, etc.)"
    )

    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        help_text="Current status of the donation"
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='claimed_donations',
        help_text="User who claimed this donation"
    )
    claimed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the donation was claimed"
    )

    # Metrics and calculations
    estimated_meals = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Estimated number of meals this donation can provide"
    )
    weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        help_text="Weight in kilograms (for reporting purposes)"
    )
    monetary_value_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Estimated monetary value in local currency"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Donation Listing"
        verbose_name_plural = "Donation Listings"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['donor']),
            models.Index(fields=['status']),
            models.Index(fields=['food_type']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['pickup_window_start', 'pickup_window_end']),
            models.Index(fields=['created_at']),
            models.Index(fields=['available_from', 'available_until']),
            models.Index(fields=['pickup_location'], name='donation_location_idx'),  # For GeoDjango if used
        ]

    def __str__(self):
        return f"{self.get_food_type_display()} - {self.quantity} {self.quantity_unit} from {self.donor.username}"

    def clean(self):
        """Custom validation"""
        super().clean()
        errors = {}

        # Validate timing
        if self.pickup_window_start and self.pickup_window_end:
            if self.pickup_window_start >= self.pickup_window_end:
                errors['pickup_window_end'] = "Pickup window end must be after start time."

        if self.expiry_date and self.pickup_window_end:
            if self.expiry_date < self.pickup_window_end:
                errors['expiry_date'] = "Expiry date must be after pickup window end."

        # Validate quantity constraints
        if self.minimum_quantity and self.maximum_quantity:
            if self.minimum_quantity > self.maximum_quantity:
                errors['maximum_quantity'] = "Maximum quantity must be greater than minimum quantity."
            if self.quantity < self.minimum_quantity:
                errors['quantity'] = f"Quantity must be at least {self.minimum_quantity} {self.quantity_unit}."
            if self.maximum_quantity and self.quantity > self.maximum_quantity:
                errors['quantity'] = f"Quantity cannot exceed {self.maximum_quantity} {self.quantity_unit}."

        # Validate that available_until is after available_from if both are set
        if self.available_from and self.available_until:
            if self.available_until <= self.available_from:
                errors['available_until'] = "Available until must be after available from."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to calculate derived fields and ensure data integrity"""
        self.clean()

        # Set available_from to now if not set
        if not self.available_from:
            self.available_from = timezone.now()

        # Set available_until to expiry_date if not explicitly set
        if not self.available_until:
            self.available_until = self.expiry_date

        # Calculate estimated meals (simplified - in reality this would depend on food type)
        if not self.estimated_meals and self.quantity:
            # Default assumption: 1kg = 4 meals (adjust based on food type in real implementation)
            meals_per_kg = 4  # This would vary by food_type
            self.estimated_meals = int(float(self.quantity) * meals_per_kg)

        # Calculate weight in kg for reporting (simplified conversion)
        if not self.weight_kg and self.quantity:
            # Simple conversion - in reality you'd need a proper conversion table
            unit_to_kg_multiplier = {
                'kg': 1,
                'grams': 0.001,
                'lbs': 0.453592,
                'ounces': 0.0283495,
                # For volume units, approximate conversion (would need density in real app)
                'liters': 1,  # Assuming water-like density
                'milliliters': 0.001,
                'pieces': 0.5,  # Rough estimate
                'portions': 0.3,  # Rough estimate
                'boxes': 10,  # Would vary greatly
                'bags': 5,  # Would vary greatly
                'containers': 2,  # Would vary greatly
                'pallets': 500,  # Would vary greatly
            }
            multiplier = unit_to_kg_multiplier.get(self.quantity_unit, 1)
            self.weight_kg = self.quantity * multiplier

        # Update donor profile if it exists
        if self.donor_profile:
            self.donor_profile.save()  # This will trigger stats update

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the donation has expired"""
        now = timezone.now()
        return now > self.expiry_date

    @property
    def is_within_pickup_window(self):
        """Check if current time is within pickup window"""
        now = timezone.now()
        return (
            self.pickup_window_start <= now <= self.pickup_window_end
        )

    @property
    def is_available_for_claiming(self):
        """Check if donation can be claimed"""
        return (
            self.status == 'available' and
            not self.is_expired and
            self.is_within_pickup_window and
            (not self.available_until or timezone.now() <= self.available_until)
        )

    def claim(self, user):
        """Mark donation as claimed by a user"""
        if not self.is_available_for_claiming:
            raise ValidationError("This donation is not available for claiming.")

        self.status = 'claimed'
        self.claimed_by = user
        self.claimed_at = timezone.now()
        self.save(update_fields=['status', 'claimed_by', 'claimed_at'])

    def cancel(self):
        """Cancel the donation"""
        if self.status in ['completed', 'cancelled']:
            raise ValidationError("Cannot donate a completed or already cancelled donation.")

        self.status = 'cancelled'
        self.save(update_fields=['status'])

    def complete(self):
        """Mark donation as completed"""
        if self.status not in ['delivered', 'picked_up']:
            raise ValidationError("Can only complete delivered or picked up donations.")

        self.status = 'completed'
        self.save(update_fields=['status'])

    @classmethod
    def get_available_donations(cls, user=None, limit=None):
        """Get available donations with optional filtering"""
        queryset = cls.objects.filter(
            status='available'
        ).exclude(
            expiry_date__lt=timezone.now()
        ).select_related('donor', 'donor_profile')

        if user:
            # Exclude user's own donations if they're a donor
            if hasattr(user, 'donor_profile'):
                queryset = queryset.exclude(donor=user)

            # Optionally filter by location/distance in future

        if limit:
            queryset = queryset[:limit]

        return queryset

    @classmethod
    def get_expiring_soon(cls, hours=24):
        """Get donations expiring within specified hours"""
        from datetime import timedelta
        expiry_threshold = timezone.now() + timedelta(hours=hours)
        return cls.objects.filter(
            status='available',
            expiry_date__lte=expiry_threshold,
            expiry_date__gt=timezone.now()
        ).select_related('donor', 'donor_profile')


class DonationImage(models.Model):
    """Separate model for donation images for better management"""
    donation = models.ForeignKey(
        DonationListing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_donation_images'
    )

    class Meta:
        verbose_name = "Donation Image"
        verbose_name_plural = "Donation Images"
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.donation}"


class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Core relationships
    donation = models.ForeignKey(
        DonationListing,
        on_delete=models.CASCADE,
        related_name='match_requests'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donation_requests'
    )
    recipient_profile = models.ForeignKey(
        'recipients.RecipientProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation_requests',
        help_text="Recipient profile (for performance optimization)"
    )

    # Request details
    message = models.TextField(
        blank=True,
        help_text="Optional message from recipient to donor"
    )
    quantity_requested = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.001,
        validators=[MinValueValidator(0.001)],
        help_text="Quantity of food requested"
    )
    quantity_unit = models.CharField(
        max_length=20,
        choices=DonationListing.UNIT_CHOICES,
        default='kg',
        help_text="Unit of measurement for requested quantity"
    )

    # Logistics
    preferred_pickup_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Preferred time for pickup/delivery"
    )
    special_instructions = models.TextField(
        blank=True,
        help_text="Special instructions for pickup/delivery"
    )

    # Status and tracking
    status = (
        models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default='pending',
            help_text="Current status of the request"
        )
    )
    responded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the donor responded to the request"
    )
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responded_requests',
        help_text="Who responded to this request (donor or admin)"
    )
    response_message = models.TextField(
        blank=True,
        help_text="Response message from donor"
    )

    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Match Request"
        verbose_name_plural = "Match Requests"
        ordering = ['-requested_at']
        unique_together = ('donation', 'recipient')
        indexes = [
            models.Index(fields=['donation']),
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['requested_at']),
            models.Index(fields=['status', 'requested_at']),
        ]

    def __str__(self):
        return f"Request from {self.recipient.username} for {self.donation}"

    def clean(self):
        """Custom validation"""
        super().clean()
        errors = {}

        # Validate that requested quantity doesn't exceed donation limits
        if self.donation:
            if self.quantity_requested < self.donation.minimum_quantity:
                errors['quantity_requested'] = f"Requested quantity must be at least {self.donation.minimum_quantity} {self.donation.quantity_unit}."

            if self.donation.maximum_quantity and self.quantity_requested > self.donation.maximum_quantity:
                errors['quantity_requested'] = f"Requested quantity cannot exceed {self.donation.maximum_quantity} {self.donation.quantity_unit}."

            # Check if units match (or are compatible)
            if self.quantity_unit != self.donation.quantity_unit:
                # In a real app, you'd want to convert between compatible units
                pass  # For now, just warn - could add conversion logic

        # Ensure recipient matches the donation's intended recipient type
        if self.recipient and self.donation.donor:
            donor_profile = getattr(self.donation.donor, 'donor_profile', None)
            recipient_profile = getattr(self.recipient, 'recipient_profile', None)

            # Add any recipient/donor compatibility checks here
            pass

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        self.clean()

        # Set quantity_unit to match donation if not set
        if self.donation and not self.quantity_unit:
            self.quantity_unit = self.donation.quantity_unit

        super().save(*args, **kwargs)

    def accept(self, user, response_message=""):
        """Accept the request"""
        if self.status != 'pending':
            raise ValidationError("Only pending requests can be accepted.")

        if user != self.donation.donor and not user.is_staff:
            raise ValidationError("Only the donor or admin can accept this request.")

        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.responded_by = user
        self.response_message = response_message

        # Update donation status
        self.donation.status = 'matched'
        self.donation.save(update_fields=['status'])

        self.save()

    def reject(self, user, response_message=""):
        """Reject the request"""
        if self.status != 'pending':
            raise ValidationError("Only pending requests can be rejected.")

        if user != self.donation.donor and not user.is_staff:
            raise ValidationError("Only the donor or admin can reject this request.")

        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.responded_by = user
        self.response_message = response_message
        self.save()

    def cancel(self, user):
        """Cancel the request"""
        if self.status not in ['pending', 'accepted']:
            raise ValidationError("Only pending or accepted requests can be cancelled.")

        if user != self.recipient and not user.is_staff:
            raise ValidationError("Only the recipient or admin can cancel this request.")

        self.status = 'cancelled'
        self.responded_at = timezone.now()
        self.responded_by = user
        self.response_message = "Cancelled by requester"
        self.save()

        # If was accepted, update donation status back to available
        if self.status == 'accepted':
            self.donation.status = 'available'
            self.donation.save(update_fields=['status'])

    def complete(self, user):
        """Mark request as completed"""
        if self.status != 'accepted':
            raise ValidationError("Only accepted requests can be completed.")

        if user != self.donation.donor and not user.is_staff:
            raise ValidationError("Only the donor or admin can mark request as completed.")

        self.status = 'completed'
        self.responded_at = timezone.now()
        self.responded_by = user
        self.response_message = "Marked as completed"

        # Update donation status
        self.donation.status = 'completed'
        self.donation.save(update_fields=['status'])

        self.save()