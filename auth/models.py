from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')

    def __str__(self):
        return self.username
