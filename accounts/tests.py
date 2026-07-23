from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()

class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model."""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'donor'
        }
        # Create a user for tests that need an existing user
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test creating a user"""
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser2'
        user_data['email'] = 'test2@example.com'
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')
        self.assertEqual(user.role, 'donor')
        self.assertTrue(user.check_password('securepassword123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_creation_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_email_normalization(self):
        """Test that email is converted to lowercase"""
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser3'
        user_data['email'] = 'TEST3@EXAMPLE.COM'
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.email, 'test3@example.com')

    def test_role_properties(self):
        """Test role property methods"""
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser_role'
        user_data['email'] = 'testrole@example.com'
        user = User.objects.create_user(**user_data)
        self.assertTrue(user.is_donor)
        self.assertFalse(user.is_recipient)
        self.assertFalse(user.is_admin)

        user.role = 'recipient'
        user.save()
        self.assertFalse(user.is_donor)
        self.assertTrue(user.is_recipient)
        self.assertFalse(user.is_admin)

        user.role = 'admin'
        user.save()
        self.assertFalse(user.is_donor)
        self.assertFalse(user.is_recipient)
        self.assertTrue(user.is_admin)

    def test_get_full_name_or_username(self):
        """Test get_full_name_or_username method"""
        # Test with first and last name
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser4'
        user_data['email'] = 'test4@example.com'
        user_data['first_name'] = 'John'
        user_data['last_name'] = 'Doe'
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.get_full_name_or_username(), 'John Doe')

        # Test with only first name
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser5'
        user_data['email'] = 'test5@example.com'
        user_data['first_name'] = 'John'
        user_data['last_name'] = ''
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.get_full_name_or_username(), 'John')

        # Test with only last name
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser6'
        user_data['email'] = 'test6@example.com'
        user_data['first_name'] = ''
        user_data['last_name'] = 'Doe'
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.get_full_name_or_username(), 'Doe')

        # Test with no names (fallback to username)
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser7'
        user_data['email'] = 'test7@example.com'
        user_data['first_name'] = ''
        user_data['last_name'] = ''
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.get_full_name_or_username(), 'testuser7')

    def test_email_required_and_unique(self):
        """Test that email is required and unique"""
        # Test email required (empty string)
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser5'
        user_data['email'] = ''
        with self.assertRaises((IntegrityError, ValidationError)):
            User.objects.create_user(**user_data)

        # Test email unique
        user_data2 = self.user_data.copy()
        user_data2['username'] = 'testuser6'
        user_data2['email'] = 'test@example.com'  # same as setUp user
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**user_data2).save()


class UserAuthenticationTest(TestCase):
    """Test cases for user authentication"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'role': 'donor'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_authentication_with_username(self):
        """Test authenticating with username"""
        user = authenticate(username='testuser', password='securepassword123')
        self.assertEqual(user, self.user)

    def test_user_authentication_with_email(self):
        """Test authenticating with email"""
        user = authenticate(username='test@example.com', password='securepassword123')
        self.assertEqual(user, self.user)

    def test_user_authentication_wrong_password(self):
        """Test authenticating with wrong password"""
        user = authenticate(username='testuser', password='wrongpassword')
        self.assertIsNone(user)

    def test_user_authentication_nonexistent_user(self):
        """Test authenticating with nonexistent user"""
        user = authenticate(username='nonexistent', password='password')
        self.assertIsNone(user)