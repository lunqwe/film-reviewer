from .models import CustomUser, Employer, Candidate, Verificator
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from common.services import *
import random


def create_user(validated_data):
    password = validated_data.pop('password2')        
    
    user = create_object(CustomUser, validated_data)
    user.set_password(password)
    user.save()
    
    accout_type = validated_data['status']
    if accout_type == 'employer':
        create_object(Employer, {'user': user})
    elif accout_type == 'candidate':
        create_object(Candidate, {'user': user})
    else:
        return get_response('error', "Wrong user status.", status=status.HTTP_400_BAD_REQUEST)

    return get_response('success', 'User created successfully!', {'id': user.id}, status=status.HTTP_201_CREATED)
    

def login_user(request, user, email, password):
    if authenticate(request=request, email=email, password=password):
                    # Если пароль валиден, создаем или получаем токен
        token, created = Token.objects.get_or_create(user=user)
        return {'status': 'success', 'token': token.key}
    else:
                    # Если пароль неверен
        return {'status': 'error', 'detail': "Invalid password"}

def send_verification(user):
    generated_code = random.randint(100000,1000000)
    try:
        verificator = Verificator.objects.filter(user=user)
        if len(verificator) == 1:
            verificator = verificator[0]
        elif len(verificator) > 1:
            raise ValueError('User has more than 1 verificator. Code error')
                        
        elif len(verificator) < 1:
            verificator = create_object(Verificator, {"user": user})
            print('create')
    except Exception as e:
        print(e)
    verificator.code = str(generated_code)
    verificator.time_created = timezone.now()
    verificator.save()
                    
    mail = send_email(user_email=user.email, subject='Jobpilot email verification', email_content=str(generated_code))
    if mail:
        return get_response('success', 'Verification message sent!', status=status.HTTP_201_CREATED)
    else:
        return get_response('error', 'Failed to send email. (401 Unauthorized) ', status=status.HTTP_408_REQUEST_TIMEOUT)