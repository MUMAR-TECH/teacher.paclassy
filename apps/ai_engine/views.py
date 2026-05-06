from datetime import datetime
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import LessonPlan, Assessment, GeneratedContent, AITutorSession, TeacherAgentSession, AdminAgentSession
from .serializers import (
    LessonPlanSerializer, LessonPlanCreateSerializer,
    AssessmentSerializer, AssessmentCreateSerializer,
    GeneratedContentSerializer, ContentCreateSerializer,
    AITutorSessionSerializer, TutorChatSerializer,
    TeacherAgentSessionSerializer, AdminAgentSessionSerializer, AgentChatSerializer,
)
from .services import ai_service
from apps.accounts.permissions import IsTeacherOrAdmin, IsStudent, IsSchoolAdmin


def _check_school(user):
    if not user.school:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('You must be associated with a school.')


def _log_usage(user, feature):
    """Record a usage event asynchronously (best-effort)."""
    try:
        from apps.analytics.models import UsageEvent
        UsageEvent.objects.create(
            user=user,
            school=user.school if user and hasattr(user, 'school') else None,
            feature=feature,
        )
    except Exception:
        pass


class LessonPlanListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        _check_school(request.user)
        plans = LessonPlan.objects.filter(teacher=request.user, school=request.user.school)
        serializer = LessonPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        _check_school(request.user)
        serializer = LessonPlanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        content = ai_service.generate_lesson_plan(
            subject=data['subject'],
            grade=data['grade'],
            duration=data['duration'],
            objectives=data['objectives'],
            curriculum=data.get('curriculum'),
        )

        plan = LessonPlan.objects.create(
            teacher=request.user,
            school=request.user.school,
            title=data['title'],
            subject=data['subject'],
            grade=data['grade'],
            duration=data['duration'],
            objectives=data['objectives'],
            content=content,
        )
        _log_usage(request.user, 'lesson_plan')
        return Response(LessonPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class LessonPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonPlanSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        _check_school(self.request.user)
        return LessonPlan.objects.filter(teacher=self.request.user, school=self.request.user.school)


class AssessmentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        _check_school(request.user)
        assessments = Assessment.objects.filter(school=request.user.school)
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    def post(self, request):
        _check_school(request.user)
        serializer = AssessmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result = ai_service.generate_assessment(
            subject=data['subject'],
            grade=data['grade'],
            assessment_type=data['assessment_type'],
            num_questions=data['num_questions'],
            difficulty=data['difficulty'],
            topic=data.get('topic'),
        )

        questions = result.get('questions', [])
        total_marks = result.get('total_marks', sum(q.get('marks', 1) for q in questions))

        assessment = Assessment.objects.create(
            teacher=request.user,
            school=request.user.school,
            title=data['title'],
            subject=data['subject'],
            grade=data['grade'],
            assessment_type=data['assessment_type'],
            num_questions=data['num_questions'],
            difficulty=data['difficulty'],
            questions=questions,
            marking_scheme=result.get('marking_scheme', {}),
            total_marks=total_marks,
        )
        _log_usage(request.user, 'assessment')
        return Response(AssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED)


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        _check_school(self.request.user)
        return Assessment.objects.filter(school=self.request.user.school)


class ContentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        _check_school(request.user)
        content = GeneratedContent.objects.filter(teacher=request.user, school=request.user.school)
        serializer = GeneratedContentSerializer(content, many=True)
        return Response(serializer.data)

    def post(self, request):
        _check_school(request.user)
        serializer = ContentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        generated = ai_service.generate_content(
            content_type=data['content_type'],
            subject=data['subject'],
            grade=data['grade'],
            topic=data['topic'],
            difficulty=data['difficulty'],
            language=data['language'],
        )

        obj = GeneratedContent.objects.create(
            teacher=request.user,
            school=request.user.school,
            content_type=data['content_type'],
            subject=data['subject'],
            grade=data['grade'],
            topic=data['topic'],
            difficulty=data['difficulty'],
            language=data['language'],
            content=generated,
        )
        _log_usage(request.user, 'content')
        return Response(GeneratedContentSerializer(obj).data, status=status.HTTP_201_CREATED)


class TutorSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        _check_school(request.user)
        sessions = AITutorSession.objects.filter(student=request.user, school=request.user.school)
        serializer = AITutorSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        _check_school(request.user)
        subject = request.data.get('subject', '')
        grade = request.data.get('grade', '')
        session = AITutorSession.objects.create(
            student=request.user,
            school=request.user.school,
            subject=subject,
            grade=grade,
            messages=[],
        )
        _log_usage(request.user, 'tutor')
        return Response(AITutorSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class TutorChatView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, pk):
        session = get_object_or_404(AITutorSession, pk=pk, student=request.user)
        serializer = TutorChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        messages = session.messages or []

        messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.utcnow().isoformat(),
        })

        openai_messages = [{'role': m['role'], 'content': m['content']} for m in messages]
        response_text = ai_service.chat_with_tutor(openai_messages, session.subject, session.grade)

        messages.append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.utcnow().isoformat(),
        })

        session.messages = messages
        session.save()

        return Response({
            'message': response_text,
            'session': AITutorSessionSerializer(session).data,
        })


class TeacherAgentSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        sessions = TeacherAgentSession.objects.filter(teacher=request.user)
        serializer = TeacherAgentSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        title = request.data.get('title', '')
        session = TeacherAgentSession.objects.create(
            teacher=request.user,
            school=request.user.school,
            title=title,
            messages=[],
        )
        _log_usage(request.user, 'teacher_agent')
        return Response(TeacherAgentSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class TeacherAgentChatView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, pk):
        session = get_object_or_404(TeacherAgentSession, pk=pk, teacher=request.user)
        serializer = AgentChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        messages = session.messages or []

        messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.utcnow().isoformat(),
        })

        # Build context from teacher profile
        subjects = []
        grades = []
        try:
            profile = request.user.teacher_profile
            subjects = profile.subjects or []
            grades = profile.grades or []
        except Exception:
            pass

        teacher_name = request.user.get_full_name() or request.user.username
        school_name = request.user.school.name if request.user.school else None

        chat_messages = [{'role': m['role'], 'content': m['content']} for m in messages]
        response_text = ai_service.chat_with_teacher_agent(
            chat_messages, teacher_name, school_name, subjects, grades
        )

        messages.append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.utcnow().isoformat(),
        })

        session.messages = messages
        session.save()

        return Response({
            'message': response_text,
            'session': TeacherAgentSessionSerializer(session).data,
        })


class AdminAgentSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        sessions = AdminAgentSession.objects.filter(admin=request.user)
        serializer = AdminAgentSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        title = request.data.get('title', '')
        session = AdminAgentSession.objects.create(
            admin=request.user,
            school=request.user.school,
            title=title,
            messages=[],
        )
        _log_usage(request.user, 'admin_agent')
        return Response(AdminAgentSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class AdminAgentChatView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def post(self, request, pk):
        session = get_object_or_404(AdminAgentSession, pk=pk, admin=request.user)
        serializer = AgentChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        messages = session.messages or []

        messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.utcnow().isoformat(),
        })

        # Build admin context from school stats
        from apps.accounts.models import User as UserModel
        school = request.user.school
        total_teachers = UserModel.objects.filter(school=school, role='teacher').count() if school else 0
        total_students = UserModel.objects.filter(school=school, role='student').count() if school else 0
        ai_credits = school.ai_credits if school and hasattr(school, 'ai_credits') else 'N/A'

        admin_name = request.user.get_full_name() or request.user.username
        school_name = school.name if school else None

        chat_messages = [{'role': m['role'], 'content': m['content']} for m in messages]
        response_text = ai_service.chat_with_admin_agent(
            chat_messages, admin_name, school_name, total_teachers, total_students, ai_credits
        )

        messages.append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.utcnow().isoformat(),
        })

        session.messages = messages
        session.save()

        return Response({
            'message': response_text,
            'session': AdminAgentSessionSerializer(session).data,
        })
