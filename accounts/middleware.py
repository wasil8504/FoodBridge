from django.conf import settings


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