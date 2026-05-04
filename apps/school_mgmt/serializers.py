from rest_framework import serializers
from .models import AttendanceRecord, TimetableEntry, ReportCard


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'school', 'class_obj', 'student', 'date', 'status', 'notes']
        read_only_fields = ['id', 'school']


class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = ['id', 'school', 'class_obj', 'day', 'start_time', 'end_time', 'subject', 'teacher', 'room']
        read_only_fields = ['id', 'school']


class ReportCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = ['id', 'student', 'school', 'academic_year', 'term', 'grades', 'ai_summary', 'generated_at']
        read_only_fields = ['id', 'school', 'ai_summary', 'generated_at']
