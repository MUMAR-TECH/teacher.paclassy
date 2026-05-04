from django.db import models


class AttendanceRecord(models.Model):
    STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='attendance_records')
    class_obj = models.ForeignKey('schools.Class', on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='present')
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['class_obj', 'student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"


class TimetableEntry(models.Model):
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='timetable_entries')
    class_obj = models.ForeignKey('schools.Class', on_delete=models.CASCADE, related_name='timetable_entries')
    day = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='timetable_entries'
    )
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.class_obj.name} - {self.day} {self.start_time}-{self.end_time}"

    class Meta:
        ordering = ['day', 'start_time']


class ReportCard(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='report_cards')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='report_cards')
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    grades = models.JSONField(default=dict)
    ai_summary = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.academic_year} {self.term}"

    class Meta:
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-generated_at']
