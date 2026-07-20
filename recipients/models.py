from django.db import models
from django.conf import settings


class RecipientProfile(models.Model):
    RECIPIENT_TYPE_CHOICES = [
        ('shelter', 'Homeless Shelter'),
        ('food_bank', 'Food Bank'),
        ('community_kitchen', 'Community Kitchen'),
        ('ngo', 'Non-Governmental Organization'),
        ('church', 'Church/Religious Organization'),
        ('school', 'School/Educational Institution'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    organization_name = models.CharField(max_length=200)
    recipient_type = models.CharField(max_length=30, choices=RECIPIENT_TYPE_CHOICES)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    registration_number = models.CharField(max_length=100, help_text="Organization registration/license number")
    contact_person = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
