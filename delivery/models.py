from django.db import models
from request.models import DonationRequest

class Delivery(models.Model):
    donation_request = models.OneToOneField(
        DonationRequest,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
        ],
        default='IN_PROGRESS'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery - {self.donation_request.donation.food_name}"
