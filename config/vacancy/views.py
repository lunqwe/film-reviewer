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
from .serializers import *
from .models import Vacancy
from .services import *
from common.services import *
from user.models import CustomUser, Employer, Candidate

class CreateVacancyView(generics.CreateAPIView):
    serializer_class = CreateVacancySerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try: 
            serializer.is_valid(raise_exception=True)
            try:
                return create_vacancy(request.data)
            except Exception as e:
                print(e)
                return get_response('error', f'Error creating vacancy ({e})', status=status.HTTP_400_BAD_REQUEST)
            
        except serializers.ValidationError as e:
            return error_detail(e) 
        