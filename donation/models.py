from django.db import models
from core.models import User

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    pickup_address = models.TextField()
    expiry_date = models.DateField()
    is_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_name
