from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .serializers import *
from .models import Vacancy
from .services import *
from common.services import *
from user.models import CustomUser, Employer, Candidate
from .models import Vacancy
from .filters import VacancyFilter
from django_filters.rest_framework import DjangoFilterBackend
from .paginators import VacancyPagination


class CreateVacancyView(generics.CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = CreateVacancySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.create(request.data)
                return get_response("success", "Vacancy created successfully!", status=status.HTTP_201_CREATED)
            else:
                return get_response("error", 'Error while creating vacancy.', status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return error_detail(e)
    
class GetVacanciesView(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = GetVacanciesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VacancyFilter
    pagination_class = VacancyPagination
        