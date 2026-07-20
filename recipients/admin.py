from django.contrib import admin
from .models import RecipientProfile

@admin.register(RecipientProfile)
class RecipientProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'recipient_type', 'is_verified', 'created_at')
    list_filter = ('recipient_type', 'is_verified', 'created_at')
    search_fields = ('organization_name', 'user__username', 'user__email', 'address', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')