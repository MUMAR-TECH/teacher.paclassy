"""
Role-isolation tests.

Verifies that:
- Teachers cannot access student routes
- Students cannot access admin routes
- Admins cannot access teacher routes
- Each role CAN access their own dashboard
- Unauthenticated users are redirected to login
"""
from django.test import TestCase
from apps.accounts.models import User


class RoleIsolationTests(TestCase):
    """
    Verify strict path-based role isolation enforced by
    RolePathMiddleware + role_required decorator.
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
        response = self.client.get('/teacher/dashboard/')
        self.assertIn(response.status_code, [302, 301])

    def test_unauthenticated_student_dashboard_redirects(self):
        response = self.client.get('/student/dashboard/')
        self.assertIn(response.status_code, [302, 301])

    def test_unauthenticated_admin_dashboard_redirects(self):
        response = self.client.get('/admin_panel/dashboard/')
        self.assertIn(response.status_code, [302, 301])

    # ---------------------------------------------------------------
    # Each role CAN access their own section
    # ---------------------------------------------------------------

    def test_teacher_can_access_teacher_dashboard(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get('/teacher/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_student_can_access_student_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/student/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin_panel/dashboard/')
        self.assertEqual(response.status_code, 200)

    # ---------------------------------------------------------------
    # Teacher CANNOT access student or admin routes
    # ---------------------------------------------------------------

    def test_teacher_cannot_access_student_dashboard(self):
        """Teacher visiting /student/dashboard/ must be redirected to /teacher/dashboard/."""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/student/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/teacher/', response['Location'])

    def test_teacher_cannot_access_admin_dashboard(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get('/admin_panel/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/teacher/', response['Location'])

    # ---------------------------------------------------------------
    # Student CANNOT access teacher or admin routes
    # ---------------------------------------------------------------

    def test_student_cannot_access_teacher_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/teacher/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/student/', response['Location'])

    def test_student_cannot_access_admin_dashboard(self):
        self.client.force_login(self.student_user)
        response = self.client.get('/admin_panel/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/student/', response['Location'])

    # ---------------------------------------------------------------
    # Admin CANNOT access teacher or student routes
    # ---------------------------------------------------------------

    def test_admin_cannot_access_teacher_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/teacher/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/admin_panel/', response['Location'])

    def test_admin_cannot_access_student_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/student/dashboard/')
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertIn('/admin_panel/', response['Location'])

    # ---------------------------------------------------------------
    # Teacher-specific AI tool routes are blocked for other roles
    # ---------------------------------------------------------------

    def test_student_cannot_access_lesson_planner(self):
        """Lesson planner is teacher-only; student must be redirected."""
        self.client.force_login(self.student_user)
        response = self.client.get('/teacher/ai/lesson-planner/')
        self.assertIn(response.status_code, [302, 403])

    def test_admin_cannot_access_lesson_planner(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/teacher/ai/lesson-planner/')
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------
    # Session login redirects to correct path section
    # ---------------------------------------------------------------

    def test_login_redirects_teacher_to_teacher_section(self):
        response = self.client.post(
            '/login/',
            {'username': 'teacher_test', 'password': 'testpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/teacher/', response['Location'])

    def test_login_redirects_student_to_student_section(self):
        response = self.client.post(
            '/login/',
            {'username': 'student_test', 'password': 'testpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/student/', response['Location'])

    def test_login_redirects_admin_to_admin_section(self):
        response = self.client.post(
            '/login/',
            {'username': 'admin_test', 'password': 'testpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin_panel/', response['Location'])
