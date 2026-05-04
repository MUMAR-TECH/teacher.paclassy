from django.db import models


class LessonPlan(models.Model):
    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='lesson_plans')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='lesson_plans')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    duration = models.IntegerField(help_text='Duration in minutes')
    objectives = models.TextField()
    content = models.JSONField(default=dict)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.teacher.username}"

    class Meta:
        ordering = ['-created_at']


class Assessment(models.Model):
    TYPES = [
        ('mcq', 'MCQ'),
        ('theory', 'Theory'),
        ('practical', 'Practical'),
        ('mixed', 'Mixed'),
    ]
    DIFFICULTY = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_assessments')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    assessment_type = models.CharField(max_length=20, choices=TYPES, default='mcq')
    num_questions = models.IntegerField(default=10)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY, default='medium')
    questions = models.JSONField(default=list)
    marking_scheme = models.JSONField(default=dict)
    total_marks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class GeneratedContent(models.Model):
    TYPES = [
        ('notes', 'Notes'),
        ('worksheet', 'Worksheet'),
        ('slides_outline', 'Slides Outline'),
    ]

    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='generated_content')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='generated_content')
    content_type = models.CharField(max_length=30, choices=TYPES)
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    topic = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, default='medium')
    language = models.CharField(max_length=50, default='English')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content_type}: {self.topic}"

    class Meta:
        ordering = ['-created_at']


class AITutorSession(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='tutor_sessions')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='tutor_sessions')
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session: {self.student.username} - {self.subject}"

    class Meta:
        ordering = ['-updated_at']
