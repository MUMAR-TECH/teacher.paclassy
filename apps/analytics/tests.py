from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.schools.models import School


class AnalyticsTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Analytics School', subdomain='analytics', email='a@test.com'
        )
        self.teacher = User.objects.create_user(
            username='analytics_teacher', password='Pass123', role='teacher', school=self.school
        )

    def test_teacher_analytics(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('teacher-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lesson_plans_created', response.data)
