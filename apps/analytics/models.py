from django.db import models


class UsageEvent(models.Model):
    FEATURE_CHOICES = [
        ('lesson_plan', 'Lesson Plan'),
        ('assessment', 'Assessment'),
        ('content', 'Content Generator'),
        ('tutor', 'AI Tutor'),
        ('teacher_agent', 'Teacher Agent'),
        ('admin_agent', 'Admin Agent'),
        ('page_view', 'Page View'),
    ]
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usage_events',
    )
    school = models.ForeignKey(
        'schools.School', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usage_events',
    )
    feature = models.CharField(max_length=30, choices=FEATURE_CHOICES)
    page = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feature', 'created_at']),
            models.Index(fields=['school', 'created_at']),
        ]

    def __str__(self):
        return f"{self.feature} by {self.user} at {self.created_at}"
