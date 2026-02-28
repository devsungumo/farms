from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add custom fields, e.g.,
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
