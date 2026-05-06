from django.conf import settings
from django.http import HttpResponseRedirect

# Maps user roles to their expected subdomain
ROLE_SUBDOMAIN_MAP = {
    'teacher': 'teacher',
    'student': 'student',
    'admin': 'admin',
}

# The set of subdomains that are role-gated (www/root are open)
ROLE_SUBDOMAINS = set(ROLE_SUBDOMAIN_MAP.values())


class RoleSubdomainMiddleware:
    """
    Middleware that compares the current subdomain with the authenticated user's
    role and redirects mismatches to the correct subdomain.

    Example: a logged-in teacher visiting student.domain.com is transparently
    redirected to teacher.domain.com (preserving the request path).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_subdomain = self._get_subdomain(request.get_host())
            if current_subdomain in ROLE_SUBDOMAINS:
                expected_subdomain = ROLE_SUBDOMAIN_MAP.get(request.user.role)
                if expected_subdomain and current_subdomain != expected_subdomain:
                    parent = getattr(settings, 'PARENT_HOST', 'localhost')
                    qs = ('?' + request.META['QUERY_STRING']) if request.META.get('QUERY_STRING') else ''
                    correct_url = (
                        f"{request.scheme}://{expected_subdomain}.{parent}{request.path}{qs}"
                    )
                    return HttpResponseRedirect(correct_url)

        return self.get_response(request)

    @staticmethod
    def _get_subdomain(host):
        """Extract the leftmost label from the host (strips port first)."""
        host = host.split(':')[0]
        parts = host.split('.')
        return parts[0] if len(parts) >= 2 else None
