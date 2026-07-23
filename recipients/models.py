from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class RecipientProfile(models.Model):
    RECIPIENT_TYPE_CHOICES = [
        ('shelter', _('Homeless Shelter')),
        ('food_bank', _('Food Bank')),
        ('community_kitchen', _('Community Kitchen')),
        ('ngo', _('Non-Governmental Organization')),
        ('church', _('Church/Religious Organization')),
        ('school', _('School/Educational Institution')),
        ('other', _('Other')),
    ]

    # Core relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='recipient_profile'
    )

    # Organization information
    organization_name = models.CharField(
        max_length=200,
        help_text="Name of the organization"
    )
    recipient_type = models.CharField(
        max_length=30,
        choices=RECIPIENT_TYPE_CHOICES,
        help_text="Type of recipient organization"
    )
    address = models.TextField(
        help_text="Physical address for delivery/pickup"
    )
    phone_number = models.CharField(
        max_length=17,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        help_text="Contact phone number"
    )
    email = models.EmailField(
        help_text="Contact email address"
    )
    registration_number = models.CharField(
        max_length=100,
        help_text="Organization registration/license number"
    )
    contact_person = models.CharField(
        max_length=100,
        help_text="Primary contact person name"
    )

    # Operational details
    capacity_per_meal = models.PositiveIntegerField(
        default=50,
        help_text="Number of people that can be served per meal"
    )
    storage_capacity_kg = models.PositiveIntegerField(
        default=100,
        help_text="Maximum food storage capacity in kilograms"
    )
    has_refrigeration = models.BooleanField(
        default=False,
        help_text="Whether the facility has refrigeration capabilities"
    )
    has_cooking_facilities = models.BooleanField(
        default=True,
        help_text="Whether the facility has cooking capabilities"
    )
    accepts_perishable = models.BooleanField(
        default=True,
        help_text="Whether the organization accepts perishable food items"
    )

    # Verification and trust metrics
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this recipient has been verified"
    )
    verification_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when verification was completed"
    )
    verification_notes = models.TextField(
        blank=True,
        help_text="Notes from verification process"
    )

    # Performance metrics
    total_requests = models.PositiveIntegerField(
        default=0,
        help_text="Total number of donation requests made"
    )
    total_food_received_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total weight of food received in kilograms"
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating from donors (0-5)"
    )
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of requests that were fulfilled (0-100)"
    )

    # Preferences and restrictions
    preferred_food_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred food types (from FOOD_TYPE_CHOICES)"
    )
    restricted_food_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of restricted food types due to allergies, religious reasons, etc."
    )
    preferred_delivery_days = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred days for delivery (0=Monday, 6=Sunday)"
    )
    preferred_delivery_time_start = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred start time for deliveries"
    )
    preferred_delivery_time_end = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred end time for deliveries"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recipient Profile"
        verbose_name_plural = "Recipient Profiles"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['recipient_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"

    def clean(self):
        """Custom validation"""
        super().clean()
        # Ensure email matches user email
        if self.email != self.user.email:
            raise ValidationError({
                'email': _("Recipient email must match user email.")
            })

        # Validate that preferred_food_types and restricted_food_types don't overlap
        if self.preferred_food_types and self.restricted_food_types:
            overlap = set(self.preferred_food_types) & set(self.restricted_food_types)
            if overlap:
                raise ValidationError({
                    'restricted_food_types': _("Food types cannot be both preferred and restricted.")
                })

    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        self.clean()
        # Update verification date if verification status changed to True
        if self.is_verified and not self.verification_date:
            from django.utils import timezone
            self.verification_date = timezone.now()
        super().save(*args, **kwargs)

    def update_request_stats(self):
        """Update request statistics"""
        from donations.models import MatchRequest

        requests = MatchRequest.objects.filter(recipient=self.user)
        fulfilled_requests = requests.filter(status__in=['accepted', 'completed'])

        self.total_requests = requests.count()
        if self.total_requests > 0:
            self.success_rate = (fulfilled_requests.count() / self.total_requests) * 100
        self.save(update_fields=['total_requests', 'success_rate'])


class RecipientServiceArea(models.Model):
    """Define geographical areas where recipients can receive donations"""
    recipient = models.ForeignKey(
        RecipientProfile,
        on_delete=models.CASCADE,
        related_name='service_areas'
    )
    area_name = models.CharField(max_length=100)
    postal_code_prefix = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recipient Service Area"
        verbose_name_plural = "Recipient Service Areas"
        unique_together = ['recipient', 'area_name']

    def __str__(self):
        return f"{self.recipient.organization_name} - {self.area_name}"