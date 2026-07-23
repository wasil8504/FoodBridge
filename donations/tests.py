from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import DonationListing, MatchRequest, DonationImage
from accounts.models import CustomUser
from donors.models import DonorProfile
from recipients.models import RecipientProfile

User = get_user_model()

class DonationListingModelTest(TestCase):
    """Test cases for DonationListing model"""

    def setUp(self):
        """Set up test data"""
        # Create donor user
        self.donor_user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

        # Create recipient user
        self.recipient_user = User.objects.create_user(
            username='recipientuser',
            email='recipient@example.com',
            password='recipientpass123',
            role='recipient'
        )

        # Create profiles
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

        self.recipient_profile = RecipientProfile.objects.create(
            user=self.recipient_user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        # Base donation data
        self.base_donation_data = {
            'donor': self.donor_user,
            'donor_profile': self.donor_profile,
            'food_type': 'prepared_meals',
            'description': 'Freshly cooked meals',
            'quantity': Decimal('10.000'),
            'quantity_unit': 'kg',
            'expiry_date': timezone.now() + timedelta(days=2),
            'pickup_location': 'Kitchen back door',
            'pickup_window_start': timezone.now() + timedelta(hours=1),
            'pickup_window_end': timezone.now() + timedelta(hours=3),
            'available_from': timezone.now(),
        }

    def test_donation_creation(self):
        """Test creating a donation listing"""
        donation = DonationListing.objects.create(**self.base_donation_data)
        self.assertEqual(donation.donor, self.donor_user)
        self.assertEqual(donation.food_type, 'prepared_meals')
        self.assertEqual(donation.quantity, Decimal('10.000'))
        self.assertEqual(donation.status, 'available')
        self.assertIsNotNone(donation.created_at)
        self.assertIsNotNone(donation.updated_at)

    def test_donation_string_representation(self):
        """Test string representation of donation"""
        donation = DonationListing.objects.create(**self.base_donation_data)
        expected_str = f"Prepared Meals - {donation.quantity} {donation.quantity_unit} from {self.donor_user.username}"
        self.assertEqual(str(donation), expected_str)

    def test_donation_clean_method_validation(self):
        """Test validation in clean method"""
        # Test pickup window validation
        invalid_data = self.base_donation_data.copy()
        invalid_data['pickup_window_start'] = timezone.now() + timedelta(hours=3)
        invalid_data['pickup_window_end'] = timezone.now() + timedelta(hours=1)  # End before start

        donation = DonationListing(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            donation.clean()
        self.assertIn('pickup_window_end', context.exception.message_dict)

        # Test expiry date validation
        invalid_data2 = self.base_donation_data.copy()
        invalid_data2['expiry_date'] = timezone.now() + timedelta(hours=1)
        invalid_data2['pickup_window_end'] = timezone.now() + timedelta(hours=2)  # Pickup ends after expiry

        donation2 = DonationListing(**invalid_data2)
        with self.assertRaises(ValidationError) as context:
            donation2.clean()
        self.assertIn('expiry_date', context.exception.message_dict)

        # Test quantity validation
        invalid_data3 = self.base_donation_data.copy()
        invalid_data3['minimum_quantity'] = Decimal('5.000')
        invalid_data3['maximum_quantity'] = Decimal('3.000')  # Max less than min

        donation3 = DonationListing(**invalid_data3)
        with self.assertRaises(ValidationError) as context:
            donation3.clean()
        self.assertIn('maximum_quantity', context.exception.message_dict)

    def test_donation_save_method(self):
        """Test save method calculations"""
        donation = DonationListing.objects.create(**self.base_donation_data)

        # Check that available_from was set if not provided
        self.assertIsNotNone(donation.available_from)

        # Check that available_until was set to expiry_date if not provided
        self.assertEqual(donation.available_until, donation.expiry_date)

        # Check that estimated_meals was calculated
        self.assertIsNotNone(donation.estimated_meals)
        # Expected: 10 kg * 4 meals/kg = 40 meals
        self.assertEqual(donation.estimated_meals, 40)

        # Check that weight_kg was calculated
        self.assertIsNotNone(donation.weight_kg)
        # For kg unit, weight_kg should equal quantity
        self.assertEqual(donation.weight_kg, donation.quantity)

    def test_donation_status_transitions(self):
        """Test donation status transitions"""
        donation = DonationListing.objects.create(**self.base_donation_data)

        # Initial status should be available
        self.assertEqual(donation.status, 'available')

        # Test claiming
        donation.status = 'claimed'
        donation.claimed_by = self.recipient_user
        donation.claimed_at = timezone.now()
        donation.save()

        refreshed_donation = DonationListing.objects.get(id=donation.id)
        self.assertEqual(refreshed_donation.status, 'claimed')
        self.assertEqual(refreshed_donation.claimed_by, self.recipient_user)
        self.assertIsNotNone(refreshed_donation.claimed_at)

    def test_donation_indexes(self):
        """Test that database indexes are defined"""
        # This test ensures the Meta indexes are defined
        # We can't easily test actual DB indexes without hitting the database,
        # but we can verify the Meta class exists
        self.assertTrue(hasattr(DonationListing, '_meta'))
        indexes = DonationListing._meta.indexes
        self.assertGreater(len(indexes), 0)


class MatchRequestModelTest(TestCase):
    """Test cases for MatchRequest model"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.donor_user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

        self.recipient_user = User.objects.create_user(
            username='recipientuser',
            email='recipient@example.com',
            password='recipientpass123',
            role='recipient'
        )

        # Create profiles
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant',
            donor_type='restaurant',
            address='123 Test Street',
            phone_number='+1234567890',
            email='donor@example.com'
        )

        self.recipient_profile = RecipientProfile.objects.create(
            user=self.recipient_user,
            organization_name='Test Shelter',
            recipient_type='shelter',
            address='456 Shelter Ave',
            phone_number='+0987654321',
            email='recipient@example.com',
            registration_number='REG123',
            contact_person='Jane Doe'
        )

        # Create donation
        self.donation = DonationListing.objects.create(
            donor=self.donor_user,
            donor_profile=self.donor_profile,
            food_type='prepared_meals',
            description='Freshly cooked meals',
            quantity=Decimal('3.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=2),
            pickup_location='Kitchen back door',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=3),
            available_from=timezone.now(),
            minimum_quantity=Decimal('1.000'),
            maximum_quantity=Decimal('5.000')
        )

    def test_match_request_creation(self):
        """Test creating a match request"""
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg',
            message='Please accept this donation',
            special_instructions='Handle with care'
        )

        self.assertEqual(request_obj.donation, self.donation)
        self.assertEqual(request_obj.recipient, self.recipient_user)
        self.assertEqual(request_obj.quantity_requested, Decimal('2.000'))
        self.assertEqual(request_obj.status, 'pending')
        self.assertIsNotNone(request_obj.requested_at)

    def test_match_request_string_representation(self):
        """Test string representation of match request"""
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )

        expected_str = f"Request from {self.recipient_user.username} for {self.donation}"
        self.assertEqual(str(request_obj), expected_str)

    def test_match_request_clean_method_validation(self):
        """Test validation in clean method"""
        # Test quantity below minimum
        request_obj = MatchRequest(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('0.500'),  # Below minimum of 1.000
            quantity_unit='kg'
        )

        with self.assertRaises(ValidationError) as context:
            request_obj.clean()
        self.assertIn('quantity_requested', context.exception.message_dict)

        # Test quantity above maximum
        request_obj2 = MatchRequest(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('10.000'),  # Above maximum of 5.000
            quantity_unit='kg'
        )

        with self.assertRaises(ValidationError) as context:
            request_obj2.clean()
        self.assertIn('quantity_requested', context.exception.message_dict)

    def test_match_request_accept(self):
        """Test accepting a match request"""
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )

        # Initially should be pending
        self.assertEqual(request_obj.status, 'pending')
        self.assertEqual(self.donation.status, 'available')

        # Accept the request
        request_obj.accept(self.donor_user, "Thank you for the donation!")

        # Check request status
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, 'accepted')
        self.assertEqual(request_obj.responded_by, self.donor_user)
        self.assertEqual(request_obj.response_message, "Thank you for the donation!")
        self.assertIsNotNone(request_obj.responded_at)

        # Check donation status
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'matched')

    def test_match_request_reject(self):
        """Test rejecting a match request"""
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )

        # Reject the request
        request_obj.reject(self.donor_user, "Sorry, already allocated")

        # Check request status
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, 'rejected')
        self.assertEqual(request_obj.responded_by, self.donor_user)
        self.assertEqual(request_obj.response_message, "Sorry, already allocated")
        self.assertIsNotNone(request_obj.responded_at)

        # Donation should remain available
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'available')

    def test_match_request_cancel(self):
        """Test cancelling a match request"""
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )

        # Cancel the request
        request_obj.cancel(self.recipient_user)

        # Check request status
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, 'cancelled')
        self.assertEqual(request_obj.responded_by, self.recipient_user)
        self.assertEqual(request_obj.response_message, "Cancelled by requester")
        self.assertIsNotNone(request_obj.responded_at)

        # Donation should remain available
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'available')

    def test_match_request_complete(self):
        """Test completing a match request"""
        # First accept the request
        request_obj = MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )
        request_obj.accept(self.donor_user)

        # Now complete it
        request_obj.complete(self.donor_user)

        # Check request status
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, 'completed')
        self.assertEqual(request_obj.responded_by, self.donor_user)
        self.assertEqual(request_obj.response_message, "Marked as completed")
        self.assertIsNotNone(request_obj.responded_at)

        # Check donation status
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'completed')

    def test_unique_together_constraint(self):
        """Test that donation-recipient pair is unique"""
        # Create first request
        MatchRequest.objects.create(
            donation=self.donation,
            recipient=self.recipient_user,
            quantity_requested=Decimal('2.000'),
            quantity_unit='kg'
        )

        # Try to create duplicate request - should fail
        with self.assertRaises(Exception):  # IntegrityError
            MatchRequest.objects.create(
                donation=self.donation,
                recipient=self.recipient_user,
                quantity_requested=Decimal('3.000'),
                quantity_unit='kg'
            )


class DonationImageModelTest(TestCase):
    """Test cases for DonationImage model"""

    def setUp(self):
        """Set up test data"""
        # Create donor user
        self.donor_user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='donorpass123',
            role='donor'
        )

        # Create donation
        self.donation = DonationListing.objects.create(
            donor=self.donor_user,
            food_type='prepared_meals',
            description='Freshly cooked meals',
            quantity=Decimal('10.000'),
            quantity_unit='kg',
            expiry_date=timezone.now() + timedelta(days=2),
            pickup_location='Kitchen back door',
            pickup_window_start=timezone.now() + timedelta(hours=1),
            pickup_window_end=timezone.now() + timedelta(hours=3),
            available_from=timezone.now(),
        )

    def test_donation_image_creation(self):
        """Test creating a donation image"""
        image = DonationImage.objects.create(
            donation=self.donation,
            uploaded_by=self.donor_user,
            image_url='https://example.com/image1.jpg',
            is_primary=True,
            caption='Main dish'
        )

        self.assertEqual(image.donation, self.donation)
        self.assertEqual(image.uploaded_by, self.donor_user)
        self.assertEqual(image.image_url, 'https://example.com/image1.jpg')
        self.assertTrue(image.is_primary)
        self.assertEqual(image.caption, 'Main dish')
        self.assertIsNotNone(image.uploaded_at)

    def test_donation_image_string_representation(self):
        """Test string representation of donation image"""
        image = DonationImage.objects.create(
            donation=self.donation,
            uploaded_by=self.donor_user,
            image_url='https://example.com/image1.jpg'
        )

        expected_str = f"Image for {self.donation}"
        self.assertEqual(str(image), expected_str)

    def test_multiple_images_with_primary(self):
        # DonationImage Model Test
        pass