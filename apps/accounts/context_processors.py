def user_role(request):
    """Injects the authenticated user's role into every template context."""
    if request.user.is_authenticated:
        return {'user_role': request.user.role}
    return {'user_role': None}
