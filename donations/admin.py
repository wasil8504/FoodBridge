from django.contrib import admin
from .models import DonationListing, MatchRequest, VerificationRequest, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(DonationListing)
class DonationListingAdmin(admin.ModelAdmin):
    list_display = ('donor', 'food_type', 'quantity', 'quantity_unit', 'status', 'expiry_date', 'created_at')
    list_filter = ('food_type', 'status', 'expiry_date', 'created_at')
    search_fields = ('donor__username', 'donor__email', 'description', 'pickup_location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('donation', 'recipient', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('donation__donor__username', 'recipient__username', 'message')
    readonly_fields = ('requested_at', 'updated_at')


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'document_type', 'status', 'submitted_at')
    list_filter = ('verification_type', 'status', 'submitted_at')
    search_fields = ('user__username', 'user__email', 'document_type', 'document_number')
    readonly_fields = ('submitted_at', 'reviewed_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'title', 'message')
    readonly_fields = ('created_at',)