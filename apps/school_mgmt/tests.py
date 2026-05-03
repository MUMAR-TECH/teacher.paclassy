from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import datetime
from apps.accounts.models import User
from apps.schools.models import School, Class
from .models import AttendanceRecord


class AttendanceTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', subdomain='attschool', email='att@test.com'
        )
        self.teacher = User.objects.create_user(
            username='att_teacher', password='Pass123', role='teacher', school=self.school
        )
        self.student = User.objects.create_user(
            username='att_student', password='Pass123', role='student', school=self.school
        )
        self.class_obj = Class.objects.create(
            school=self.school, name='Class 7A', grade='Grade 7',
            teacher=self.teacher, academic_year='2024'
        )

    def test_create_attendance(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('attendance-list')
        data = {
            'class_obj': self.class_obj.id,
            'student': self.student.id,
            'date': str(datetime.date.today()),
            'status': 'present',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceRecord.objects.count(), 1)
