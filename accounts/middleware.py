from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import hashlib


class LoginRateLimitMiddleware:
    """
    Middleware to rate limit login attempts.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Get settings for rate matching from settings.py
        self.enabled = getattr(settings, 'LOGIN_RATE_LIMIT_ENABLED', True)
        self.max_attempts = getattr(settings, 'LOGIN_ATTEMPT_LIMIT', 5)
        self.window_seconds = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 300)  # seconds
        self.block_seconds = getattr(settings, 'LOGIN_BLOCK_TIME', 900)  # seconds

    def __call__(self, request):
        # Only apply to login attempts
        if self.enabled and request.path == '/admin/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            username = request.POST.get('username', '')

            # Create a unique key for this IP and username
            key = f"login_attempt_{ip}_{username}"
            # Key for blocked flag
            block_key = f"login_blocked_{ip}_{username}"

            # Check if the IP/username is currently blocked
            if cache.get(block_key):
                # If blocked, return a 429 response
                from django.http import HttpResponse
                return HttpResponse("Too many login attempts. Please try again later.", status=429)

            # Process the request
            response = self.get_response(request)

            # If the response is successful (status code 200) and contains a success message,
            # we can reset the attempt count. However, for simplicity, we'll just clear on any response.
            # In a more advanced implementation, we would check if the login was successful.
            # For now, we'll increment on every attempt and reset on success (if we can detect it).
            # Since we don't have easy access to the login success, we'll just increment.

            # Increment the attempt count
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, timeout=self.window_seconds)

            # If attempts exceed the limit, block the IP/username
            if attempts >= self.max_attempts:
                cache.set(block_key, True, timeout=self.block_seconds)

            return response

        # For other requests, just continue
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSPMiddleware:
    """
    Middleware to add Content Security Policy headers to responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Get CSP policy from settings, default to empty dict if not configured
        self.csp_policy = getattr(settings, 'CONTENT_SECURITY_POLICY', {})

    def __call__(self, request):
        response = self.get_response(request)

        # Only add CSP header if policy is defined and not in DEBUG mode
        # (in development, CSP might interfere with debug tools)
        if self.csp_policy and not getattr(settings, 'DEBUG', True):
            csp_header = self._build_csp_header()
            if csp_header:
                response['Content-Security-Policy'] = csp_header

        return response

    def _build_csp_header(self):
        """Build the CSP header string from the policy dictionary."""
        if not self.csp_policy:
            return ''

        directives = []
        for directive, value in self.csp_policy.items():
            if value:  # Only add directive if it has a value
                directives.append(f"{directive} {value}")

        return '; '.join(directives)