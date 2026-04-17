from django.contrib import admin
from .models import JobApplication, StatusHistory

# Register your models here.
admin.site.register(JobApplication)
admin.site.register(StatusHistory)