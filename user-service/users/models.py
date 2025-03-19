from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class LibraryUser(AbstractUser):
    address = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "Library User"
        verbose_name_plural = "Library Users"
