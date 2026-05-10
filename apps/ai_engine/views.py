import io
from datetime import datetime
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
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
        plans = LessonPlan.objects.filter(teacher=request.user)
        serializer = LessonPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
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

        school = getattr(request.user, 'school', None)
        plan = LessonPlan.objects.create(
            teacher=request.user,
            school=school,
            title=data['title'],
            subject=data['subject'],
            grade=data['grade'],
            duration=data['duration'],
            objectives=data['objectives'],
            content=content,
        )
        _log_usage(request.user, 'lesson_plan')
        return Response(LessonPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class LessonPlanDownloadView(APIView):
    """Download a lesson plan as Word (.docx) or PDF."""
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request, pk, fmt):
        plan = get_object_or_404(LessonPlan, pk=pk, teacher=request.user)
        if fmt == 'docx':
            return self._as_docx(plan)
        elif fmt == 'pdf':
            return self._as_pdf(plan)
        return Response({'detail': 'Invalid format. Use docx or pdf.'}, status=400)

    # ------------------------------------------------------------------ #
    def _as_docx(self, plan):
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        c = plan.content if isinstance(plan.content, dict) else {}

        # Title
        title_para = doc.add_heading(plan.title, level=0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Meta
        meta = doc.add_paragraph()
        meta.add_run(f'Subject: {plan.subject}  |  Grade: {plan.grade}  |  Duration: {plan.duration} min').bold = True

        doc.add_paragraph()  # spacer

        # Overview
        if c.get('overview'):
            doc.add_heading('Overview', level=1)
            doc.add_paragraph(c['overview'])

        # Objectives
        if c.get('objectives'):
            doc.add_heading('Learning Objectives', level=1)
            for obj in c['objectives']:
                doc.add_paragraph(obj, style='List Bullet')

        # Materials
        if c.get('materials'):
            doc.add_heading('Materials', level=1)
            for mat in c['materials']:
                doc.add_paragraph(mat, style='List Bullet')

        # Lesson Sections
        if c.get('sections'):
            doc.add_heading('Lesson Sections', level=1)
            for section in c['sections']:
                doc.add_heading(f"{section.get('name', '')} ({section.get('duration', '')} min)", level=2)
                for act in section.get('activities', []):
                    doc.add_paragraph(act, style='List Bullet')
                if section.get('teacher_notes'):
                    note = doc.add_paragraph()
                    note.add_run('Teacher Notes: ').bold = True
                    note.add_run(section['teacher_notes'])

        # Assessment
        if c.get('assessment'):
            doc.add_heading('Assessment', level=1)
            doc.add_paragraph(c['assessment'])

        # Homework
        if c.get('homework'):
            doc.add_heading('Homework', level=1)
            doc.add_paragraph(c['homework'])

        # Differentiation
        if c.get('differentiation'):
            doc.add_heading('Differentiation', level=1)
            diff = c['differentiation']
            if diff.get('support'):
                p = doc.add_paragraph()
                p.add_run('Support: ').bold = True
                p.add_run(diff['support'])
            if diff.get('extension'):
                p = doc.add_paragraph()
                p.add_run('Extension: ').bold = True
                p.add_run(diff['extension'])

        # If AI returned raw text only
        if c.get('raw') and not c.get('sections'):
            doc.add_heading('Lesson Plan Content', level=1)
            doc.add_paragraph(c['raw'])

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        filename = f"lesson_plan_{plan.pk}.docx"
        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # ------------------------------------------------------------------ #
    def _as_pdf(self, plan):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        indigo = colors.HexColor('#4f46e5')

        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                     textColor=indigo, fontSize=20, spaceAfter=6)
        h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
                                  textColor=indigo, fontSize=13, spaceBefore=14, spaceAfter=4)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                                  fontSize=11, spaceBefore=10, spaceAfter=3)
        body_style = styles['BodyText']
        body_style.leading = 14

        story = []
        c = plan.content if isinstance(plan.content, dict) else {}

        story.append(Paragraph(plan.title, title_style))
        story.append(Paragraph(
            f'<b>Subject:</b> {plan.subject} &nbsp; <b>Grade:</b> {plan.grade} &nbsp; <b>Duration:</b> {plan.duration} min',
            body_style
        ))
        story.append(Spacer(1, 12))

        if c.get('overview'):
            story.append(Paragraph('Overview', h1_style))
            story.append(Paragraph(c['overview'], body_style))

        if c.get('objectives'):
            story.append(Paragraph('Learning Objectives', h1_style))
            items = [ListItem(Paragraph(o, body_style)) for o in c['objectives']]
            story.append(ListFlowable(items, bulletType='bullet'))

        if c.get('materials'):
            story.append(Paragraph('Materials', h1_style))
            items = [ListItem(Paragraph(m, body_style)) for m in c['materials']]
            story.append(ListFlowable(items, bulletType='bullet'))

        if c.get('sections'):
            story.append(Paragraph('Lesson Sections', h1_style))
            for section in c['sections']:
                story.append(Paragraph(
                    f"{section.get('name', '')} <font color='grey'>({section.get('duration', '')} min)</font>",
                    h2_style
                ))
                if section.get('activities'):
                    items = [ListItem(Paragraph(a, body_style)) for a in section['activities']]
                    story.append(ListFlowable(items, bulletType='bullet'))
                if section.get('teacher_notes'):
                    story.append(Paragraph(
                        f'<b>Teacher Notes:</b> {section["teacher_notes"]}', body_style
                    ))

        if c.get('assessment'):
            story.append(Paragraph('Assessment', h1_style))
            story.append(Paragraph(c['assessment'], body_style))

        if c.get('homework'):
            story.append(Paragraph('Homework', h1_style))
            story.append(Paragraph(c['homework'], body_style))

        if c.get('differentiation'):
            story.append(Paragraph('Differentiation', h1_style))
            diff = c['differentiation']
            if diff.get('support'):
                story.append(Paragraph(f'<b>Support:</b> {diff["support"]}', body_style))
            if diff.get('extension'):
                story.append(Paragraph(f'<b>Extension:</b> {diff["extension"]}', body_style))

        if c.get('raw') and not c.get('sections'):
            story.append(Paragraph('Lesson Plan Content', h1_style))
            for line in c['raw'].split('\n'):
                if line.strip():
                    story.append(Paragraph(line, body_style))

        doc.build(story)
        buf.seek(0)
        filename = f"lesson_plan_{plan.pk}.pdf"
        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class LessonPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonPlanSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return LessonPlan.objects.filter(teacher=self.request.user)


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
