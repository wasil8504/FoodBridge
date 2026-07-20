from django import forms
from .models import DonationListing

class DonationListingForm(forms.ModelForm):
    class Meta:
        model = DonationListing
        fields = [
            'food_type', 'description', 'quantity', 'quantity_unit',
            'expiry_date', 'pickup_location', 'pickup_window_start', 'pickup_window_end', 'photos'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'pickup_window_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'pickup_window_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'photos': forms.URLInput(attrs={'placeholder': 'Comma-separated URLs or JSON array'}),
        }
        help_texts = {
            'photos': 'Enter a comma-separated list of image URLs or a JSON array of URLs.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set input formats for datetime fields to match the HTML5 datetime-local input
        self.fields['expiry_date'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['pickup_window_start'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['pickup_window_end'].input_formats = ('%Y-%m-%dT%H:%M',)

    def clean_photos(self):
        photos = self.cleaned_data.get('photos')
        # If it's a string, we assume it's comma-separated URLs and convert to list
        if isinstance(photos, str):
            # Split by comma and strip whitespace
            photos_list = [url.strip() for url in photos.split(',') if url.strip()]
            return photos_list
        # If it's already a list (from JSON), return as is
        return photos