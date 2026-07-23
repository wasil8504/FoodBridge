from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
        ('admin', 'Admin'),
    )

    # Override email to make it required and unique
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='donor',
        help_text="User role determines permissions and accessible features"
    )

    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )

    address = models.TextField(
        blank=True,
        null=True,
        help_text="Physical address"
    )

    # Email verification fields
    email_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this user has verified their email address"
    )

    # Profile completion tracking
    profile_completed = models.BooleanField(
        default=False,
        help_text="Designates whether the user has completed their profile"
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the user was created"
    )

    updated_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the user was last updated"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'role']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def clean(self):
        """Custom validation"""
        super().clean()
        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower()
        else:
            raise ValidationError({'email': 'Email is required.'})

    def save(self, *args, **kwargs):
        """Override save to ensure data integrity"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_donor(self):
        return self.role == 'donor'

    @property
    def is_recipient(self):
        return self.role == 'recipient'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_full_name_or_username(self):
        """Return full name if available, otherwise username"""
        return f"{self.first_name} {self.last_name}".strip() or self.username