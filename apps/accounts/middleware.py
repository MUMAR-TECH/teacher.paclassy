from django.http import HttpResponseRedirect

# Maps role to its URL path prefix
ROLE_PATH_MAP = {
    'teacher': '/teacher/dashboard/',
    'student': '/student/dashboard/',
    'admin': '/admin_panel/dashboard/',
}

# Path prefixes that are role-gated
ROLE_PATH_PREFIXES = {
    '/teacher/': 'teacher',
    '/student/': 'student',
    '/admin_panel/': 'admin',
}


class RolePathMiddleware:
    """
    Middleware that checks if an authenticated user is accessing a path
    that belongs to a different role, and redirects them to their own section.

    Example: a logged-in teacher visiting /student/dashboard/ is transparently
    redirected to /teacher/dashboard/ (preserving UX without a 403).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            for prefix, required_role in ROLE_PATH_PREFIXES.items():
                if path.startswith(prefix):
                    if request.user.role != required_role:
                        correct_url = ROLE_PATH_MAP.get(request.user.role, '/login/')
                        return HttpResponseRedirect(correct_url)
                    break

        return self.get_response(request)
