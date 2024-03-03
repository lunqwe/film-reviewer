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
        fields = ['user']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'user_id']


class CreateVacancySerializer(serializers.ModelSerializer):
    employer = EmployerSerializer()

    class Meta:
        model = Vacancy
        fields = '__all__'

    def create(self, validated_data):
        user_id = validated_data.pop('employer').get('user').id
        employer = get_obj_by_user_id(Employer, user_id)
        return Vacancy.objects.create(employer=employer, **validated_data)






class GetVacanciesSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True)
    employer = EmployerSerializer()

    class Meta:
        model = Vacancy
        fields = "__all__"



    
"""

get all jobs (candidate)
get employer jobs (employer)

vision type (highlight, always top)

aply for job (candidate)


"""