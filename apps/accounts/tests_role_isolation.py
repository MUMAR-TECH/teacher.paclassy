"""
Role-isolation tests.

Verifies that:
- Teachers cannot access student routes
- Students cannot access admin routes
- Admins cannot access teacher routes
- Each role CAN access their own dashboard
- Unauthenticated users are redirected to login
"""
from django.test import TestCase, override_settings
from apps.accounts.models import User

TEACHER_HOST = 'teacher.localhost'
STUDENT_HOST = 'student.localhost'
ADMIN_HOST = 'admin.localhost'


@override_settings(
    PARENT_HOST='localhost',
    ROOT_HOSTCONF='paclassy.hosts',
    DEFAULT_HOST='root',
)
class RoleIsolationTests(TestCase):
    """
    Verify strict subdomain role isolation enforced by
    RoleSubdomainMiddleware + role_required decorator.
    """

    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='teacher_test', password='testpass123', role='teacher',
            email='teacher@test.com'
        )
        self.student_user = User.objects.create_user(
            username='student_test', password='testpass123', role='student',
            email='student@test.com'
        )
        self.admin_user = User.objects.create_user(
            username='admin_test', password='testpass123', role='admin',
            email='admin@test.com'
        )

    # ---------------------------------------------------------------
    # Unauthenticated access should redirect to login
    # ---------------------------------------------------------------

    def test_unauthenticated_teacher_dashboard_redirects(self):
        response = self.client.get('/dashboard/', HTTP_HOST=TEACHER_HOST)
        self.assertIn(response.status_code, [302, 301])

    def test_unauthenticated_student_dashboard_redirects(self):
        response = self.client.get('/dashboard/', HTTP_HOST=STUDENT_HOST)
        self.assertIn(response.status_code, [302, 301])

    def test_unauthenticated_admin_dashboard_redirects(self):
        response = self.client.get('/dashboard/', HTTP_HOST=ADMIN_HOST)
        self.assertIn(response.status_code, [302, 301])

    # ---------------------------------------------------------------
    # Each role CAN access their own subdomain
    # ---------------------------------------------------------------

    def test_teacher_can_access_teacher_dashboard(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get('/dashboard/', HTTP_HOST=TEACHER_HOST)
        self.assertEqual(response.status_code, 200)

    def test_student_can_access_student_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/dashboard/', HTTP_HOST=STUDENT_HOST)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/dashboard/', HTTP_HOST=ADMIN_HOST)
        self.assertEqual(response.status_code, 200)

    # ---------------------------------------------------------------
    # Teacher CANNOT access student or admin routes
    # ---------------------------------------------------------------

    def test_teacher_cannot_access_student_dashboard(self):
        """Teacher visiting student.localhost/dashboard/ must be redirected."""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/dashboard/', HTTP_HOST=STUDENT_HOST)
        # Middleware redirects or decorator returns 403
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('teacher.localhost', response['Location'])

    def test_teacher_cannot_access_admin_dashboard(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get('/dashboard/', HTTP_HOST=ADMIN_HOST)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('teacher.localhost', response['Location'])

    # ---------------------------------------------------------------
    # Student CANNOT access teacher or admin routes
    # ---------------------------------------------------------------

    def test_student_cannot_access_teacher_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/dashboard/', HTTP_HOST=TEACHER_HOST)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('student.localhost', response['Location'])

    def test_student_cannot_access_admin_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/dashboard/', HTTP_HOST=ADMIN_HOST)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('student.localhost', response['Location'])

    # ---------------------------------------------------------------
    # Admin CANNOT access teacher or student routes
    # ---------------------------------------------------------------

    def test_admin_cannot_access_teacher_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/dashboard/', HTTP_HOST=TEACHER_HOST)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('admin.localhost', response['Location'])

    def test_admin_cannot_access_student_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/dashboard/', HTTP_HOST=STUDENT_HOST)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('admin.localhost', response['Location'])

    # ---------------------------------------------------------------
    # Teacher-specific AI tool routes are blocked for other roles
    # ---------------------------------------------------------------

    def test_student_cannot_access_lesson_planner(self):
        """Lesson planner is teacher-only; student must get 403."""
        self.client.force_login(self.student_user)
        response = self.client.get('/ai/lesson-planner/', HTTP_HOST=TEACHER_HOST)
        self.assertIn(response.status_code, [302, 403])

    def test_admin_cannot_access_lesson_planner(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/ai/lesson-planner/', HTTP_HOST=TEACHER_HOST)
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------
    # Session login redirects to correct subdomain
    # ---------------------------------------------------------------

    def test_login_redirects_teacher_to_teacher_subdomain(self):
        response = self.client.post(
            '/login/',
            {'username': 'teacher_test', 'password': 'testpass123'},
            HTTP_HOST='localhost',
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('teacher.localhost', response['Location'])

    def test_login_redirects_student_to_student_subdomain(self):
        response = self.client.post(
            '/login/',
            {'username': 'student_test', 'password': 'testpass123'},
            HTTP_HOST='localhost',
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('student.localhost', response['Location'])

    def test_login_redirects_admin_to_admin_subdomain(self):
        response = self.client.post(
            '/login/',
            {'username': 'admin_test', 'password': 'testpass123'},
            HTTP_HOST='localhost',
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('admin.localhost', response['Location'])
