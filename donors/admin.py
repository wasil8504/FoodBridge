from django.contrib import admin
from .models import DonorProfile

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'donor_type', 'is_verified', 'created_at')
    list_filter = ('donor_type', 'is_verified', 'created_at')
    search_fields = ('organization_name', 'user__username', 'user__email', 'address')
    readonly_fields = ('created_at', 'updated_at')