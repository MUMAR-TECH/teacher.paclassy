from rest_framework import serializers
from .models import LessonPlan, Assessment, GeneratedContent, AITutorSession, TeacherAgentSession, AdminAgentSession


class LessonPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonPlan
        fields = [
            'id', 'teacher', 'school', 'title', 'subject', 'grade',
            'duration', 'objectives', 'content', 'is_edited',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'teacher', 'school', 'content', 'created_at', 'updated_at']


class LessonPlanCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100)
    grade = serializers.CharField(max_length=20)
    duration = serializers.IntegerField(min_value=1)
    objectives = serializers.CharField()
    curriculum = serializers.CharField(required=False, default='Standard')


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            'id', 'teacher', 'school', 'title', 'subject', 'grade',
            'assessment_type', 'num_questions', 'difficulty', 'questions',
            'marking_scheme', 'total_marks', 'created_at',
        ]
        read_only_fields = ['id', 'teacher', 'school', 'questions', 'marking_scheme', 'total_marks', 'created_at']


class AssessmentCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100)
    grade = serializers.CharField(max_length=20)
    assessment_type = serializers.ChoiceField(choices=['mcq', 'theory', 'practical', 'mixed'])
    num_questions = serializers.IntegerField(min_value=1, max_value=50, default=10)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'], default='medium')
    topic = serializers.CharField(required=False)


class GeneratedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedContent
        fields = [
            'id', 'teacher', 'school', 'content_type', 'subject', 'grade',
            'topic', 'difficulty', 'language', 'content', 'created_at',
        ]
        read_only_fields = ['id', 'teacher', 'school', 'content', 'created_at']


class ContentCreateSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(choices=['notes', 'worksheet', 'slides_outline'])
    subject = serializers.CharField(max_length=100)
    grade = serializers.CharField(max_length=20)
    topic = serializers.CharField(max_length=200)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'], default='medium')
    language = serializers.CharField(default='English')


class AITutorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITutorSession
        fields = ['id', 'student', 'school', 'subject', 'grade', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'student', 'school', 'messages', 'created_at', 'updated_at']


class TutorChatSerializer(serializers.Serializer):
    message = serializers.CharField()


class TeacherAgentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAgentSession
        fields = ['id', 'teacher', 'school', 'title', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'school', 'messages', 'created_at', 'updated_at']


class AdminAgentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAgentSession
        fields = ['id', 'admin', 'school', 'title', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'admin', 'school', 'messages', 'created_at', 'updated_at']


class AgentChatSerializer(serializers.Serializer):
    message = serializers.CharField()
