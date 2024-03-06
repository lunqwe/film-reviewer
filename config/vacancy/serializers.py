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
from user.models import Candidate, Employer
from .models import Vacancy
from .services import *
from common.services import *

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['user', 'logo', 'map_location']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['user']


class CreateVacancySerializer(serializers.ModelSerializer):
    employer = EmployerSerializer()

    class Meta:
        model = Vacancy
        fields = '__all__'

    def create(self, validated_data):
        user_id = validated_data.pop('employer').get('user')
        employer = get_obj_by_user_id(Employer, user_id)
        return Vacancy.objects.create(employer=employer, **validated_data)


class GetVacanciesSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True)
    employer = EmployerSerializer()

    class Meta:
        model = Vacancy
        fields = ['employer', 'min_salery', 'max_salery', 'status', 'job_type']

class ExactVacancySerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True)
    employer = EmployerSerializer()

    class Meta:
        model = Vacancy
        fields = "__all__"



class ApplyToVacancySerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    vacancy_id = serializers.CharField(required=True)

    def create(self, validated_data):
        candidate = get_obj_by_user_id(Candidate, user_id=validated_data.get('user_id'))
        vacancy = get_object(Vacancy, **{'id': validated_data.get('vacancy_id')})

        vacancy.candidates.add(candidate)
        return Vacancy




    