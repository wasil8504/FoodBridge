from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class DonorProfile(models.Model):
    DONOR_TYPE_CHOICES = [
        ('restaurant', _('Restaurant')),
        ('grocery', _('Grocery Store')),
        ('event', _('Event Organizer')),
        ('individual', _('Individual')),
        ('other', _('Other')),
    ]

    # Core relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='donor_profile'
    )

    # Business/Organization information
    organization_name = models.CharField(
        max_length=200,
        help_text="Name of the organization or individual"
    )
    donor_type = models.CharField(
        max_length=20,
        choices=DONOR_TYPE_CHOICES,
        help_text="Type of donor organization"
    )
    address = models.TextField(
        help_text="Physical address for pickup/delivery"
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
    license_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Food handling license or registration number (if applicable)"
    )

    # Verification and trust metrics
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this donor has been verified"
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
    total_donations = models.PositiveIntegerField(
        default=0,
        help_text="Total number of donations made"
    )
    total_food_donated_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total weight of food donated in kilograms"
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating from recipients (0-5)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Donor Profile"
        verbose_name_plural = "Donor Profiles"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['donor_type']),
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
                'email': _("Donor email must match user email.")
            })

    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        self.clean()
        # Update verification date if verification status changed to True
        if self.is_verified and not self.verification_date:
            from django.utils import timezone
            self.verification_date = timezone.now()
        super().save(*args, **kwargs)

    def update_donation_stats(self):
        """Update donation statistics"""
        from donations.models import DonationListing

        donations = DonationListing.objects.filter(
            donor=self.user,
            status__in=['completed', 'picked_up']
        )

        self.total_donations = donations.count()
        # Calculate total weight by summing weight_kg of all donations
        total_weight = sum((donation.weight_kg or 0) for donation in donations)
        self.total_food_donated_kg = total_weight
        self.save(update_fields=['total_donations', 'total_food_donated_kg'])


class DonorServiceArea(models.Model):
    """Define geographical areas where donations can be made"""
    donor = models.ForeignKey(
        DonorProfile,
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
        verbose_name = "Donor Service Area"
        verbose_name_plural = "Donor Service Areas"
        unique_together = ['donor', 'area_name']

    def __str__(self):
        return f"{self.donor.organization_name} - {self.area_name}"