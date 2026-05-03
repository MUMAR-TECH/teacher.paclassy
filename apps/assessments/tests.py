from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.schools.models import School
from apps.ai_engine.models import Assessment
from .models import StudentSubmission


class SubmissionTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', subdomain='tschool', email='ts@test.com'
        )
        self.teacher = User.objects.create_user(
            username='teacher2', password='Pass123', role='teacher', school=self.school
        )
        self.student = User.objects.create_user(
            username='student1', password='Pass123', role='student', school=self.school
        )
        self.assessment = Assessment.objects.create(
            teacher=self.teacher,
            school=self.school,
            title='Math Test',
            subject='Math',
            grade='Grade 7',
            assessment_type='mcq',
            num_questions=2,
            difficulty='easy',
            questions=[
                {'id': 1, 'type': 'mcq', 'question': 'Q1?', 'correct_answer': 'A', 'marks': 1},
                {'id': 2, 'type': 'mcq', 'question': 'Q2?', 'correct_answer': 'B', 'marks': 1},
            ],
            total_marks=2,
        )

    def test_submission_and_grading(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('submission-list')
        data = {
            'assessment': self.assessment.id,
            'answers': {'1': 'A', '2': 'B'},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 2.0)
        self.assertTrue(response.data['is_graded'])

    def test_duplicate_submission_rejected(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('submission-list')
        data = {'assessment': self.assessment.id, 'answers': {'1': 'A'}}
        self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
