from django.db import models

# Create your models here.
class Vacancy(models.Model):
    author = models.ForeignKey('user.Employer', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    tags = models.JSONField(default=list)
    
    #salery
    min_salery = models.CharField(max_length=255)
    max_salery = models.CharField(max_length=255)
    salery_type = models.CharField(max_length=255)
    
    #advance info
    education = models.CharField(max_length=255)
    experience = models.CharField(max_length=255)
    job_type = models.CharField(max_length=255)
    vanancies = models.CharField(max_length=255)
    expiration_date = models.CharField(max_length=255)
    job_level = models.CharField(max_length=255)
    
    #description and responsibility 
    description = models.TextField()
    responsibilities = models.TextField()
    
    def __str__(self):
        return f'{self.title}({self.author.user.username})'
    
    