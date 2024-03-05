import django_filters
from .models import Vacancy

class VacancyFilter(django_filters.FilterSet):
    employer = django_filters.CharFilter(field_name='employer__user__id')
    candidate = django_filters.CharFilter(field_name='candidates__user__id')

    class Meta:
        model = Vacancy
        fields = ['employer', 'candidates']