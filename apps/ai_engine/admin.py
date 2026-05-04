from django.contrib import admin
from .models import LessonPlan, Assessment, GeneratedContent, AITutorSession


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'grade', 'teacher', 'created_at']
    list_filter = ['subject', 'grade']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'grade', 'assessment_type', 'difficulty', 'created_at']
    list_filter = ['assessment_type', 'difficulty', 'subject']


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ['topic', 'content_type', 'subject', 'grade', 'created_at']
    list_filter = ['content_type', 'subject']


@admin.register(AITutorSession)
class AITutorSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'grade', 'created_at']
    list_filter = ['subject']
