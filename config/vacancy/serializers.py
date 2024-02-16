from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .models import Vacancy
from .services import *
from common.services import *


class CreateVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['title', 'tags', 'min_salery', 'max_salery', 'salery_type', 'education', 'experience', 'job_type', 'vaсancies', 'expiration_date', 'job_level', 'description', 'responsibilities']
        
    def create(self, data):
        return create_object(Vacancy, data)