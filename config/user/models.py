from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, username=None, status=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, username = username, status=status, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password, full_name=None, status=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, full_name, username, status, password, **extra_fields)
        
        
class CustomUser(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, default='', blank=True, null=True)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=255, default='', blank=True, null=True)
    verified_email = models.BooleanField(default=False)
    verification_code = models.CharField(default=0)
    
    objects = CustomUserManager()
    
