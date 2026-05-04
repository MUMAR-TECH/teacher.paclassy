from django.utils.functional import SimpleLazyObject
from .models import School


def get_school_from_request(request):
    host = request.get_host().split(':')[0]
    parts = host.split('.')
    if len(parts) >= 3:
        subdomain = parts[0]
        try:
            return School.objects.get(subdomain=subdomain, is_active=True)
        except School.DoesNotExist:
            pass
    return None


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.school = SimpleLazyObject(lambda: get_school_from_request(request))
        return self.get_response(request)
