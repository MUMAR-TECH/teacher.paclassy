from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import StudentSubmission
from .serializers import StudentSubmissionSerializer
from apps.ai_engine.models import Assessment


class SubmissionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'student':
            submissions = StudentSubmission.objects.filter(student=user)
        elif user.role in ('teacher', 'admin'):
            if user.school:
                submissions = StudentSubmission.objects.filter(assessment__school=user.school)
            else:
                submissions = StudentSubmission.objects.none()
        else:
            submissions = StudentSubmission.objects.none()
        serializer = StudentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        assessment_id = request.data.get('assessment')
        assessment = get_object_or_404(Assessment, pk=assessment_id)
        answers = request.data.get('answers', {})

        if StudentSubmission.objects.filter(student=request.user, assessment=assessment).exists():
            return Response({'detail': 'Already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        score = None
        ai_feedback = {}
        is_graded = False

        if assessment.assessment_type == 'mcq':
            correct = 0
            total = 0
            for q in assessment.questions:
                qid = str(q.get('id', ''))
                if qid in answers:
                    total += q.get('marks', 1)
                    if answers[qid] == q.get('correct_answer'):
                        correct += q.get('marks', 1)
            score = correct
            is_graded = True

        submission = StudentSubmission.objects.create(
            student=request.user,
            assessment=assessment,
            answers=answers,
            score=score,
            is_graded=is_graded,
            graded_at=timezone.now() if is_graded else None,
            ai_feedback=ai_feedback,
        )
        return Response(StudentSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)


class SubmissionDetailView(generics.RetrieveAPIView):
    serializer_class = StudentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return StudentSubmission.objects.filter(student=user)
        return StudentSubmission.objects.filter(assessment__school=user.school)
