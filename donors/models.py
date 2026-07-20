from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class DonorProfile(models.Model):
    DONOR_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('grocery', 'Grocery Store'),
        ('event', 'Event Organizer'),
        ('individual', 'Individual'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    organization_name = models.CharField(max_length=200)
    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    license_number = models.CharField(max_length=100, blank=True, null=True, help_text="Food handling license or registration number")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
