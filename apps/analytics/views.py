from datetime import timedelta
from django.db.models import Avg, Count
from django.utils import timezone
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
        school = user.school
        total_teachers = User.objects.filter(school=school, role='teacher').count()
        total_students = User.objects.filter(school=school, role='student').count()
        total_assessments = Assessment.objects.filter(school=school).count()
        total_lessons = LessonPlan.objects.filter(school=school).count()
        attendance_qs = AttendanceRecord.objects.filter(school=school)
        present_count = attendance_qs.filter(status='present').count()
        total_attendance = attendance_qs.count()

        # Active users in last 24 hours (users with usage events)
        from apps.analytics.models import UsageEvent
        since_24h = timezone.now() - timedelta(hours=24)
        active_users_24h = (
            UsageEvent.objects.filter(school=school, created_at__gte=since_24h)
            .values('user')
            .distinct()
            .count()
        )

        # AI feature usage breakdown
        feature_usage = (
            UsageEvent.objects.filter(school=school)
            .values('feature')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        feature_breakdown = {item['feature']: item['count'] for item in feature_usage}

        return Response({
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_assessments': total_assessments,
            'total_lesson_plans': total_lessons,
            'attendance_rate': round(present_count / total_attendance * 100, 1) if total_attendance else 0,
            'ai_credits_remaining': school.ai_credits,
            'active_users_24h': active_users_24h,
            'feature_usage': feature_breakdown,
        })


class AdminAnalyticsChartView(APIView):
    """Returns chart-ready time-series data for the admin dashboard."""
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        user = request.user
        if not user.school:
            return Response({'detail': 'No school associated.'})

        from apps.analytics.models import UsageEvent
        school = user.school
        days = int(request.query_params.get('days', 14))
        since = timezone.now() - timedelta(days=days)

        # Daily usage counts per feature over `days` days
        events = (
            UsageEvent.objects.filter(school=school, created_at__gte=since)
            .values('feature', 'created_at__date')
            .annotate(count=Count('id'))
            .order_by('created_at__date')
        )

        # Build date labels
        date_labels = [
            (timezone.now() - timedelta(days=i)).strftime('%b %d')
            for i in range(days - 1, -1, -1)
        ]

        # Aggregate by feature and date
        features = ['lesson_plan', 'assessment', 'content', 'tutor', 'teacher_agent', 'admin_agent']
        series = {f: [0] * days for f in features}
        start_date = (timezone.now() - timedelta(days=days - 1)).date()
        for event in events:
            feat = event['feature']
            if feat in series:
                offset = (event['created_at__date'] - start_date).days
                if 0 <= offset < days:
                    series[feat][offset] += event['count']

        # User growth (teachers + students by join date)
        from apps.accounts.models import User
        user_growth = (
            User.objects.filter(school=school, date_joined__gte=since)
            .values('date_joined__date')
            .annotate(count=Count('id'))
            .order_by('date_joined__date')
        )
        growth_by_date = {str(r['date_joined__date']): r['count'] for r in user_growth}
        user_growth_series = []
        for i in range(days - 1, -1, -1):
            d = (timezone.now() - timedelta(days=i)).date()
            user_growth_series.append(growth_by_date.get(str(d), 0))

        return Response({
            'labels': date_labels,
            'feature_series': series,
            'user_growth': user_growth_series,
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
