from django.db import models

# Create your models here.
class Director(models.Model): #
    name = models.CharField(max_length=255, default='')

    def __str__(self):
        return f'{self.name}'
    

class Actor(models.Model): #
    name = models.CharField(max_length=255, default='')
    movies = models.ManyToManyField("Movie", related_name="actors")

    def __str__(self):
        return f'{self.name}'

class Movie(models.Model): 
    title = models.CharField(max_length=200)
    year_released = models.CharField(max_length=100)
    director = models.ForeignKey(Director, on_delete=models.CASCADE, related_name='movies')

    def __str__(self):
        return f'{self.title} ({self.year_released})'

