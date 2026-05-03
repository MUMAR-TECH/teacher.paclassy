from django.db import models


class School(models.Model):
    name = models.CharField(max_length=200)
    subdomain = models.SlugField(unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    plan = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('basic', 'Basic'), ('premium', 'Premium')],
        default='free'
    )
    ai_credits = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20)
    subject = models.CharField(max_length=100, blank=True)
    teacher = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='teaching_classes'
    )
    students = models.ManyToManyField(
        'accounts.User', related_name='enrolled_classes', blank=True
    )
    academic_year = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.school.name}"

    class Meta:
        verbose_name_plural = 'Classes'
        ordering = ['name']
