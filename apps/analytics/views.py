from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsTeacherOrAdmin, IsSchoolAdmin
from apps.school_mgmt.models import AttendanceRecord
from apps.ai_engine.models import LessonPlan, Assessment
from apps.assessments.models import StudentSubmission


class TeacherAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        user = request.user
        if not user.school:
            return Response({'detail': 'No school associated.'})

        lesson_plans = LessonPlan.objects.filter(teacher=user, school=user.school).count()
        assessments = Assessment.objects.filter(teacher=user, school=user.school).count()
        submissions = StudentSubmission.objects.filter(assessment__teacher=user).count()
        avg_score = StudentSubmission.objects.filter(
            assessment__teacher=user, is_graded=True
        ).aggregate(avg=Avg('score'))['avg']

        return Response({
            'lesson_plans_created': lesson_plans,
            'assessments_created': assessments,
            'total_submissions': submissions,
            'average_score': round(avg_score, 2) if avg_score else None,
        })


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        user = request.user
        if not user.school:
            return Response({'detail': 'No school associated.'})

        from apps.accounts.models import User
        total_teachers = User.objects.filter(school=user.school, role='teacher').count()
        total_students = User.objects.filter(school=user.school, role='student').count()
        total_assessments = Assessment.objects.filter(school=user.school).count()
        attendance_rate = AttendanceRecord.objects.filter(
            school=user.school, status='present'
        ).count()
        total_attendance = AttendanceRecord.objects.filter(school=user.school).count()

        return Response({
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_assessments': total_assessments,
            'attendance_rate': round(attendance_rate / total_attendance * 100, 1) if total_attendance else 0,
            'ai_credits_remaining': user.school.ai_credits,
        })


class StudentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        submissions = StudentSubmission.objects.filter(student=user)
        total = submissions.count()
        graded = submissions.filter(is_graded=True)
        avg_score = graded.aggregate(avg=Avg('score'))['avg']
        attendance = AttendanceRecord.objects.filter(student=user)
        present_count = attendance.filter(status='present').count()
        total_attendance = attendance.count()

        return Response({
            'total_submissions': total,
            'graded_submissions': graded.count(),
            'average_score': round(avg_score, 2) if avg_score else None,
            'attendance_rate': round(present_count / total_attendance * 100, 1) if total_attendance else 0,
        })
