import django_filters
from .models import Vacancy

class VacancyFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='company_name')
    candidate = django_filters.CharFilter(field_name='candidates__id')

    class Meta:
        model = Vacancy
        fields = ['employer_id', 'candidates']