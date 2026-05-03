from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from .models import School


class SchoolTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            subdomain='testschool',
            email='school@test.com',
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='AdminPass123',
            role='admin',
            school=self.school,
            is_staff=True,
        )

    def test_school_creation_and_multi_tenancy(self):
        self.assertEqual(self.school.subdomain, 'testschool')
        self.assertEqual(self.admin_user.school, self.school)

    def test_school_list_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('school-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
