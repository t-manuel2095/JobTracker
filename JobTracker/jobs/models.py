from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interview", "Interview"),
        ("offer", "Offer"),
        ("rejected", "Rejected"),
    ]

# Create your models here.
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="applied")
    applied_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['-applied_date']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def __str__(self): 
        return self.company

class StatusHistory(models.Model):
    job = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Status History'
        verbose_name_plural = 'Status Histories'

    def __str__(self):
        return f"{self.job.company} - {self.old_status} → {self.new_status}"