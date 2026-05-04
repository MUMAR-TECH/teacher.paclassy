from rest_framework import serializers
from .models import School, Class


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id', 'name', 'subdomain', 'email', 'phone', 'address',
            'logo', 'is_active', 'plan', 'ai_credits', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = [
            'id', 'school', 'name', 'grade', 'subject', 'teacher',
            'students', 'academic_year',
        ]
        read_only_fields = ['id']
