from django.contrib import admin
from .models import School, Class


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'plan', 'ai_credits', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active']
    search_fields = ['name', 'subdomain']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'school', 'teacher', 'academic_year']
    list_filter = ['school', 'grade']
