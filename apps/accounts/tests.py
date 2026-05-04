from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserRegistrationTest(APITestCase):
    def test_register_teacher(self):
        url = reverse('register')
        data = {
            'username': 'teacher1',
            'email': 'teacher1@test.com',
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'role': 'teacher',
            'first_name': 'Test',
            'last_name': 'Teacher',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'teacher2',
            'email': 'teacher2@test.com',
            'password': 'TestPass123',
            'password2': 'WrongPass123',
            'role': 'teacher',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123',
            role='teacher'
        )

    def test_login_success(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'TestPass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'WrongPass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_generation(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'TestPass123'})
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
