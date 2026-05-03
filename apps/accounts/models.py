from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    TEACHER = 'teacher'
    STUDENT = 'student'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=TEACHER)
    school = models.ForeignKey(
        'schools.School', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='members'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

    @property
    def is_student(self):
        return self.role == self.STUDENT

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    subjects = models.JSONField(default=list)
    grades = models.JSONField(default=list)
    qualifications = models.TextField(blank=True)

    def __str__(self):
        return f"Teacher Profile: {self.user.username}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_contact = models.CharField(max_length=20, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"
