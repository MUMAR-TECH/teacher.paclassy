from django.contrib import admin
from .models import AttendanceRecord, TimetableEntry, ReportCard


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_obj', 'date', 'status']
    list_filter = ['status', 'date']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'day', 'start_time', 'end_time', 'subject', 'teacher']
    list_filter = ['day', 'school']


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'generated_at']
    list_filter = ['academic_year', 'term']
