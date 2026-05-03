from django.db import models


class StudentSubmission(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='submissions')
    assessment = models.ForeignKey('ai_engine.Assessment', on_delete=models.CASCADE, related_name='submissions')
    answers = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    ai_feedback = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title}"

    class Meta:
        unique_together = ['student', 'assessment']
        ordering = ['-submitted_at']
