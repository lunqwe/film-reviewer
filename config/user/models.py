from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


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
    
    objects = CustomUserManager()
    
class Verificator(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default='0')
    time_created = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() >= self.time_created + timezone.timedelta(hours=3)
    
    def __str__(self):
        return self.user.username
    
class Employer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='media/logo', blank=True, null=True)
    banner = models.ImageField(upload_to='media/banners', blank=True, null=True)
    company_name = models.CharField(max_length=255, default="0")
    about = models.TextField(blank=True, null=True, default='0')
    
    organization_type = models.CharField(max_length=255, default='0')
    industry_types = models.CharField(max_length=255, default='0')
    team_size = models.CharField(max_length=255, default='0')
    website = models.CharField(null=True, blank=True, default='0')
    year_of_establishment = models.DateField(blank=True, null=True)
    company_vision = models.TextField(blank=True, null=True, default='0')
    
    map_location = models.CharField(max_length=255, blank=True, null=True, default='0')
    phone_number = models.CharField(max_length=30, default='0')
    email = models.EmailField(blank=True, null=True)
    def __str__(self):
        return f'{self.company_name}({self.user.username})'

class EmployerSocialLink(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    social_network = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    
    

class Candidate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='candidate/profile_pics', blank=True, null=True)
    full_name = models.CharField(max_length=255, default='0')
    headline = models.CharField(max_length=255, default='0')
    experiences = models.CharField(max_length=999, default='0')
    educations = models.CharField(max_length=999, default='0')
    website = models.CharField(max_length=999, default='0')
    
    nationality = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=255, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    
    map_location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    
    #notifications
    shortlist = models.BooleanField(default=False)
    expire = models.BooleanField(default=False)
    five_job_alerts = models.BooleanField(default=False)
    profile_saved = models.BooleanField(default=False)
    rejection = models.BooleanField(default=False)
    
    profile_privacy = models.BooleanField(default=False)
    resume_privacy = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.id}({self.user.username})'
    
    
class CandidateJobAlertNotification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    role = models.CharField(max_length=255),
    location = models.CharField(max_length=255)
    
    
    
class ResumeFile(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='candidate/resumes', blank=True, null=True)
    
class CandidateSocialLink(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    social_network = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)

    
    