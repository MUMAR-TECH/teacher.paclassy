from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.schools.models import School
from .models import LessonPlan, Assessment


class AIEngineTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', subdomain='test', email='test@test.com'
        )
        self.teacher = User.objects.create_user(
            username='teacher', password='Pass123', role='teacher', school=self.school
        )
        self.client.force_authenticate(user=self.teacher)

    def test_lesson_plan_creation_with_mock(self):
        url = reverse('lesson-plan-list')
        data = {
            'title': 'Photosynthesis Lesson',
            'subject': 'Biology',
            'grade': 'Grade 8',
            'duration': 45,
            'objectives': 'Students will understand photosynthesis',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonPlan.objects.count(), 1)

    def test_assessment_creation_with_mock(self):
        url = reverse('assessment-list')
        data = {
            'title': 'Photosynthesis Quiz',
            'subject': 'Biology',
            'grade': 'Grade 8',
            'assessment_type': 'mcq',
            'num_questions': 5,
            'difficulty': 'medium',
            'topic': 'Photosynthesis',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assessment.objects.count(), 1)

    def test_lesson_plan_list(self):
        LessonPlan.objects.create(
            teacher=self.teacher, school=self.school,
            title='Test Plan', subject='Math', grade='Grade 7',
            duration=45, objectives='Learn algebra', content={}
        )
        url = reverse('lesson-plan-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
