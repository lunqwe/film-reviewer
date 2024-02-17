from django.db import models

# Create your models here.
class Vacancy(models.Model):
    author = models.ForeignKey('user.Employer', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='')
    tags = models.JSONField(default=list)
    
    #salery
    min_salery = models.CharField(max_length=255, default='')
    max_salery = models.CharField(max_length=255, default='')
    salery_type = models.CharField(max_length=255, default='')
    
    #advance info
    education = models.CharField(max_length=255, default='')
    experience = models.CharField(max_length=255, default='')
    job_type = models.CharField(max_length=255, default='')
    vaсancies = models.CharField(max_length=255, default='')
    expiration_date = models.CharField(max_length=255, default='')
    job_level = models.CharField(max_length=255, default='')
    
    #description and responsibility 
    description = models.TextField(default='')
    responsibilities = models.TextField(default='')
    
    def __str__(self):
        return f'{self.title}({self.author.user.username})'
    
    