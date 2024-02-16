from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Vacancy
from .serializers import CreateVanancySerializer

class CreateVacancy(generics.CreateAPIView):
    serializer_class = CreateVanancySerializer
    
    def create(self, *args, **kwargs):
        pass