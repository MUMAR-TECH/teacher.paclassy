from rest_framework import serializers
from .models import StudentSubmission


class StudentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubmission
        fields = [
            'id', 'student', 'assessment', 'answers', 'score', 'feedback',
            'ai_feedback', 'submitted_at', 'graded_at', 'is_graded',
        ]
        read_only_fields = ['id', 'student', 'score', 'ai_feedback', 'submitted_at', 'graded_at', 'is_graded']
