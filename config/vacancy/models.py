from django.db import models

# Create your models here.
class Vacancy(models.Model):
    employer = models.ForeignKey('user.Employer', on_delete=models.CASCADE, related_name='vacancys')
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
    expiration_date = models.CharField(max_length=255, default='')
    job_level = models.CharField(max_length=255, default='')
    
    #description and responsibility 
    description = models.TextField(default='')
    responsibilities = models.TextField(default='')
    created_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=50, default='active')
    candidates = models.ManyToManyField('user.Candidate', related_name='jobs', blank=True)
    
    """
    def is_expired(self):
        return timezone.now() >= self.time_created + timezone.timedelta(hours=3)
    """

    def __str__(self):
        return f'{self.title}({self.employer.user.username})'
    
class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    candidate = models.ForeignKey('user.Candidate', on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    class Meta:
        unique_together = ('vacancy', 'candidate')
    