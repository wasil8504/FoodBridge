from django.db import models
from core.models import User
from donation.models import Donation

class DonationRequest(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ngo_requests')
    assigned_volunteer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteer_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('ASSIGNED', 'Assigned'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donation.food_name} - {self.status}"
