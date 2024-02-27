import django_filters
from .models import Movie

class MovieFilter(django_filters.FilterSet):
    year_released = django_filters.NumberFilter(field_name='year_released')
    director = django_filters.CharFilter(field_name='director__name', lookup_expr='icontains')
    actors = django_filters.CharFilter(field_name='actors__name', lookup_expr='icontains')

    class Meta:
        model = Movie
        fields = ['year_released', 'director', 'actors']