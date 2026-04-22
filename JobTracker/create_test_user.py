#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobTracker.settings')
django.setup()

from django.contrib.auth.models import User

user, created = User.objects.get_or_create(username='temp1')
user.set_password('temp1')
user.save()

print('[SUCCESS] Test user created/updated')
print('Username: temp1')
print('Password: temp1')
