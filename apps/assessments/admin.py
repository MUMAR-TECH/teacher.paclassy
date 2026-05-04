from django.contrib import admin
from .models import StudentSubmission


@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'score', 'is_graded', 'submitted_at']
    list_filter = ['is_graded', 'assessment__subject']
