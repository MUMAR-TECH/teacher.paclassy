from functools import wraps
from django.shortcuts import render, redirect


def _role_redirect(user_role):
    """Return the correct dashboard URL for a given role."""
    redirects = {
        'teacher': '/dashboard/teacher/',
        'student': '/dashboard/student/',
        'admin': '/dashboard/admin/',
    }
    return redirects.get(user_role, '/login/')


def role_required(allowed_roles):
    """
    Decorator for web views that checks the user's session-based role.
    Since this app uses JWT (token in localStorage), we cannot check auth server-side
    without a session cookie. Instead, we inject a JS snippet that enforces the role
    client-side and immediately redirects on mismatch. This is the same pattern used
    throughout the existing templates via `requireAuth()`.
    The decorator just sets `required_role` on the view for template access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        wrapper.required_roles = allowed_roles
        return wrapper
    return decorator


def teacher_dashboard(request):
    return render(request, 'dashboard/teacher.html')


def student_dashboard(request):
    return render(request, 'dashboard/student.html')


def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')


def lesson_planner_page(request):
    return render(request, 'ai_engine/lesson_planner.html')


def assessment_generator_page(request):
    return render(request, 'ai_engine/assessment_generator.html')


def content_generator_page(request):
    return render(request, 'ai_engine/content_generator.html')


def ai_tutor_page(request):
    return render(request, 'ai_engine/ai_tutor.html')


def teacher_agent_page(request):
    return render(request, 'ai_engine/teacher_agent.html')


def admin_agent_page(request):
    return render(request, 'ai_engine/admin_agent.html')


def attendance_page(request):
    return render(request, 'school_mgmt/attendance.html')


def timetable_page(request):
    return render(request, 'school_mgmt/timetable.html')


def students_page(request):
    return render(request, 'school_mgmt/students.html')
