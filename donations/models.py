from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


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

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Match'),
        ('matched', 'Matched'),
        ('claimed', 'Claimed'),
        ('picked_up', 'Picked Up'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    food_type = models.CharField(max_length=20, choices=FOOD_TYPE_CHOICES)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    quantity_unit = models.CharField(max_length=20, help_text="e.g., kg, lbs, portions, boxes")
    expiry_date = models.DateTimeField()
    pickup_location = models.TextField()
    pickup_window_start = models.DateTimeField()
    pickup_window_end = models.DateTimeField()
    photos = models.JSONField(default=list, blank=True, help_text="List of photo URLs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_type} - {self.quantity} {self.quantity_unit} from {self.donor.username}"

    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date

    @property
    def is_within_pickup_window(self):
        now = timezone.now()
        return self.pickup_window_start <= now <= self.pickup_window_end


class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    donation = models.ForeignKey(DonationListing, on_delete=models.CASCADE, related_name='match_requests')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donation_requests')
    message = models.TextField(blank=True, help_text="Optional message from recipient to donor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('donation', 'recipient')

    def __str__(self):
        return f"Request from {self.recipient.username} for {self.donation}"


class VerificationRequest(models.Model):
    VERIFICATION_TYPE_CHOICES = [
        ('donor', 'Donor Verification'),
        ('recipient', 'Recipient Verification'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES)
    document_type = models.CharField(max_length=100, help_text="Type of document submitted (license, registration, etc.)")
    document_number = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_verifications')
    notes = models.TextField(blank=True, help_text="Admin notes on verification decision")

    def __str__(self):
        return f"{self.verification_type} verification for {self.user.username}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('match_request', 'New Match Request'),
        ('match_accepted', 'Match Accepted'),
        ('match_rejected', 'Match Rejected'),
        ('donation_claimed', 'Donation Claimed'),
        ('donation_expired', 'Donation Expiration Warning'),
        ('status_update', 'Status Update'),
        ('system_notification', 'System Notification'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_donation = models.ForeignKey(DonationListing, on_delete=models.CASCADE, null=True, blank=True, related_name='related_notifications')
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When this notification expires/dismisses")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"