from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # We keep the default username field
    # Adding extra fields required for User Administration
    role = models.CharField(max_length=50, default='Admin')
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.username