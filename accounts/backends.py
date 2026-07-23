from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


class EmailAuthBackend(BaseBackend):
    """
    Authentication backend that allows users to log in using either
    their username or email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        # Determine if the input is an email or username
        try:
            validate_email(username)
            # It's an email, look up user by email
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce timing difference
                # but don't actually use it (just to prevent user enumeration)
                User().set_password(password)
                return None
        except ValidationError:
            # Not an email, treat as username
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce timing difference
                User().set_password(password)
                return None

        # Check the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None