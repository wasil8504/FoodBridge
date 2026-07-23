from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import DonorProfile, DonorServiceArea
from accounts.models import CustomUser

User = get_user_model()

class DonorProfileModelTest(TestCase):
    """Test cases for DonorProfile model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

    def test_donor_profile_creation(self):
        """Test creating a donor profile"""
        profile = DonorProfile.objects.create(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.organization_name, 'Test Restaurant')
        self.assertEqual(profile.donor_type, 'restaurant')
        self.assertEqual(profile.address, '123 Test Street')
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.email, 'donor@example.com')
        self.assertFalse(profile.is_verified)  # Default value
        self.assertEqual(profile.total_donations, 0)  # Default value
        self.assertEqual(profile.total_food_donated_kg, Decimal('0.00'))  # Default value
        self.assertEqual(profile.average_rating, Decimal('0.00'))  # Default value

    def test_donor_profile_string_representation(self):
        """Test string representation of donor profile"""
        profile = DonorProfile.objects.create(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

        expected_str = f"{profile.organization_name} ({self.user.username})"
        self.assertEqual(str(profile), expected_str)

    def test_donor_profile_clean_method_validation(self):
        """Test validation in clean method"""
        # Test email mismatch validation
        profile = DonorProfile(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='different@example.com'  # Different from user email
        )

        with self.assertRaises(ValidationError) as context:
            profile.clean()
        self.assertIn('email', context.exception.message_dict)

    def test_donor_profile_save_method(self):
        """Test save method updates verification date"""
        profile = DonorProfile.objects.create(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com',
            is_verified=False
        )

        # Initially no verification date
        self.assertIsNone(profile.verification_date)

        # Update to verified
        profile.is_verified = True
        profile.save()

        # Refresh from database
        profile.refresh_from_db()
        self.assertIsNotNone(profile.verification_date)
        # Should be set to approximately now
        self.assertLessEqual(
            (timezone.now() - profile.verification_date).total_seconds(),
            5  # Within 5 seconds
        )

    def test_donor_profile_update_donation_stats(self):
        """Test updating donation statistics"""
        from donations.models import DonationListing

        profile = DonorProfile.objects.create(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

        # Create some donations
        donation1 = DonationListing.objects.create(
            donor=self.user,
            food_type='prepared_meals',
            description='Test donation 1',
            quantity=Decimal('5.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=1),
            pickup_location='Location 1',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=2),
            available_from=timezone.now(),
            status='completed'
        )

        donation2 = DonationListing.objects.create(
            donor=self.user,
            food_type='fresh_produce',
            description='Test donation 2',
            quantity=Decimal('3.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=1),
            pickup_location='Location 2',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=2),
            available_from=timezone.now(),
            status='completed'
        )

        # Update stats
        initial_total = profile.total_donations
        initial_weight = profile.total_food_donated_kg

        profile.update_donation_stats()

        # Refresh from database
        profile.refresh_from_db()

        # Should have 2 donations
        self.assertEqual(profile.total_donations, 2)
        # Weight should be 8.000 kg (5 + 3)
        self.assertEqual(profile.total_food_donated_kg, Decimal('8.000'))

class DonorServiceAreaModelTest(TestCase):
    """Test cases for DonorServiceArea model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

        self.profile = DonorProfile.objects.create(
            user=self.user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

    def test_donor_service_area_creation(self):
        """Test creating a donor service area"""
        service_area = DonorServiceArea.objects.create(
            donor=self.profile,
            area_name='Downtown Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country',
            is_active=True
        )

        self.assertEqual(service_area.donor, self.profile)
        self.assertEqual(service_area.area_name, 'Downtown Area')
        self.assertEqual(service_area.postal_code_prefix, '12345')
        self.assertEqual(service_area.city, 'Test City')
        self.assertEqual(service_area.state_province, 'Test State')
        self.assertEqual(service_area.country, 'Test Country')
        self.assertTrue(service_area.is_active)
        self.assertIsNotNone(service_area.created_at)

    def test_donor_service_area_string_representation(self):
        """Test string representation of donor service area"""
        service_area = DonorServiceArea.objects.create(
            donor=self.profile,
            area_name='Downtown Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country'
        )

        expected_str = f"{self.profile.organization_name} - {service_area.area_name}"
        self.assertEqual(str(service_area), expected_str)

    def test_unique_together_constraint(self):
        """Test that donor-area_name pair is unique"""
        DonorServiceArea.objects.create(
            donor=self.profile,
            area_name='Downtown Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country'
        )

        # Try to create duplicate - should fail
        with self.assertRaises(Exception):  # IntegrityError
            DonorServiceArea.objects.create(
                donor=self.profile,
                area_name='Downtown Area',  # Same area name
                postal_code_prefix='67890',
                city='Another City',
                state_province='Another State',
                country='Another Country'
            )