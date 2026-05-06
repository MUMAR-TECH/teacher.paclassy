from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(role):
    """
    Decorator for web views that enforces server-side role-based access control.

    Usage::

        @role_required('teacher')
        def my_view(request): ...

    Unauthenticated visitors are redirected to LOGIN_URL.
    Authenticated users whose role does not match receive a 403 response.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
            if request.user.role != role:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1>"
                    "<p>You do not have permission to access this page.</p>"
                )
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
