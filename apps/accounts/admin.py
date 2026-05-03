from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherProfile, StudentProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'school', 'is_active']
    list_filter = ['role', 'is_active', 'school']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Paclassy', {'fields': ('role', 'school', 'phone', 'avatar', 'bio')}),
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'qualifications']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade', 'enrollment_date']
