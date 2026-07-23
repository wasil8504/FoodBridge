from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import RecipientProfile, RecipientServiceArea
from accounts.models import CustomUser

User = get_user_model()

class RecipientProfileModelTest(TestCase):
    """Test cases for RecipientProfile model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='recipientuser',
            email='recipient@example.com',
            password='recipientpass123',
            role='recipient'
        )

    def test_recipient_profile_creation(self):
        """Test creating a recipient profile"""
        profile = RecipientProfile.objects.create(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.organization_name, 'Test Shelter')
        self.assertEqual(profile.recipient_type, 'shelter')
        self.assertEqual(profile.address, '456 Shelter Ave')
        self.assertEqual(profile.phone_number, '+0987654321')
        self.assertEqual(profile.email, 'recipient@example.com')
        self.assertEqual(profile.registration_number, 'REG123')
        self.assertEqual(profile.contact_person, 'Jane Doe')
        self.assertEqual(profile.capacity_per_meal, 50)  # Default value
        self.assertEqual(profile.storage_capacity_kg, 100)  # Default value
        self.assertFalse(profile.has_refrigeration)  # Default value
        self.assertTrue(profile.has_cooking_facilities)  # Default value
        self.assertTrue(profile.accepts_perishable)  # Default value
        self.assertFalse(profile.is_verified)  # Default value
        self.assertEqual(profile.total_requests, 0)  # Default value
        self.assertEqual(profile.total_food_received_kg, Decimal('0.00'))  # Default value
        self.assertEqual(profile.average_rating, Decimal('0.00'))  # Default value
        self.assertEqual(profile.success_rate, Decimal('0.00'))  # Default value

    def test_recipient_profile_string_representation(self):
        """Test string representation of recipient profile"""
        profile = RecipientProfile.objects.create(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        expected_str = f"{profile.organization_name} ({self.user.username})"
        self.assertEqual(str(profile), expected_str)

    def test_recipient_profile_clean_method_validation(self):
        """Test validation in clean method"""
        # Test email mismatch validation
        profile = RecipientProfile(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='different@example.com',  # Different from user email
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        with self.assertRaises(ValidationError) as context:
            profile.clean()
        self.assertIn('email', context.exception.message_dict)

        # Test overlapping preferred and restricted food types
        profile2 = RecipientProfile(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe',
            preferred_food_types=['prepared_meals', 'fresh_produce'],
            restricted_food_types=['fresh_produce', 'dairy']  # fresh_produce appears in both
        )

        with self.assertRaises(ValidationError) as context:
            profile2.clean()
        self.assertIn('restricted_food_types', context.exception.message_dict)

    def test_recipient_profile_save_method(self):
        """Test save method updates verification date"""
        profile = RecipientProfile.objects.create(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe',
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

    def test_recipient_profile_update_request_stats(self):
        """Test updating request statistics"""
        from donations.models import MatchRequest, DonationListing
        from accounts.models import CustomUser

        # Create recipient profile
        profile = RecipientProfile.objects.create(
            user=self.user,
            organization_name='Test Shel',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        # Create donor user and donations
        donor_user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

        # Create multiple donations to allow multiple requests from same recipient
        donation1 = DonationListing.objects.create(
            donor=donor_user,
            food_type='prepared_meals',
            description='Test donation 1',
            quantity=Decimal('10.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=1),
            pickup_location='Location 1',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=2),
            available_from=timezone.now()
        )

        donation2 = DonationListing.objects.create(
            donor=donor_user,
            food_type='fresh_produce',
            description='Test donation 2',
            quantity=Decimal('5.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=1),
            pickup_location='Location 2',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=2),
            available_from=timezone.now()
        )

        donation3 = DonationListing.objects.create(
            donor=donor_user,
            food_type='bakery',
            description='Test donation 3',
            quantity=Decimal('3.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=1),
            pickup_location='Location 3',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=2),
            available_from=timezone.now()
        )

        # Create some requests
        request1 = MatchRequest.objects.create(
            donation=donation1,
            recipient=self.user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg',
            status='pending'
        )

        request2 = MatchRequest.objects.create(
            donation=donation2,
            recipient=self.user,
            quantity_requested=Decimal('3.000'),
            quantity_unit='kg',
            status='completed'
        )

        request3 = MatchRequest.objects.create(
            donation=donation3,
            recipient=self.user,
            quantity_requested=Decimal('1.000'),
            quantity_unit='kg',
            status='cancelled'
        )

        # Update stats
        initial_requests = profile.total_requests
        initial_success_rate = profile.success_rate

        profile.update_request_stats()

        # Refresh from database
        profile.refresh_from_db()

        # Should have 3 total requests
        self.assertEqual(profile.total_requests, 3)
        # Should have 1 successful request (completed)
        # Success rate = (1/3) * 100 = 33.33
        self.assertAlmostEqual(float(profile.success_rate), 33.33, places=2)

class RecipientServiceAreaModelTest(TestCase):
    """Test cases for RecipientServiceArea model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='recipientuser',
            email='recipient@example.com',
            password='recipientpass123',
            role='recipient'
        )

        self.profile = RecipientProfile.objects.create(
            user=self.user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

    def test_recipient_service_area_creation(self):
        """Test creating a recipient service area"""
        service_area = RecipientServiceArea.objects.create(
            recipient=self.profile,
            area_name='Downtown Service Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country',
            is_active=True
        )

        self.assertEqual(service_area.recipient, self.profile)
        self.assertEqual(service_area.area_name, 'Downtown Service Area')
        self.assertEqual(service_area.postal_code_prefix, '12345')
        self.assertEqual(service_area.city, 'Test City')
        self.assertEqual(service_area.state_province, 'Test State')
        self.assertEqual(service_area.country, 'Test Country')
        self.assertTrue(service_area.is_active)
        self.assertIsNotNone(service_area.created_at)

    def test_recipient_service_area_string_representation(self):
        """Test string representation of recipient service area"""
        service_area = RecipientServiceArea.objects.create(
            recipient=self.profile,
            area_name='Downtown Service Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country'
        )

        expected_str = f"{self.profile.organization_name} - {service_area.area_name}"
        self.assertEqual(str(service_area), expected_str)

    def test_unique_together_constraint(self):
        """Test that recipient-area_name pair is unique"""
        RecipientServiceArea.objects.create(
            recipient=self.profile,
            area_name='Downtown Area',
            postal_code_prefix='12345',
            city='Test City',
            state_province='Test State',
            country='Test Country'
        )

        # Try to create duplicate - should fail
        with self.assertRaises(Exception):  # IntegrityError
            RecipientServiceArea.objects.create(
                recipient=self.profile,
                area_name='Downtown Area',  # Same area name
                postal_code_prefix='67890',
                city='Another City',
                state_province='Another State',
                country='Another Country'
            )