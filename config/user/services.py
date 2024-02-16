from .models import CustomUser, Employer, Candidate, Verificator
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
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
    
    
def check_verification(validated_data):
    code = validated_data['code']
    user = get_object(CustomUser, id=validated_data['user_id'])
    if user.verified_email:
        return get_response('error', 'User email is already verified.', status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            verificator = get_object(Verificator, user=user)
            expired = verificator.is_expired()

                    # True if expired, else False
            if not expired:
                print(code, verificator.code)
                if code == verificator.code:
                    user.verified_email = True
                    verificator.delete()
                    check_verification = 'success'
                else:
                    check_verification = 'wrong_code'
            else:
                verificator.delete()
                check_verification = 'expired'
                

            if check_verification == 'expired':
                return get_response('error', 'Verification code expired.', status=status.HTTP_408_REQUEST_TIMEOUT)
                    
            elif check_verification == 'wrong_code':
                return get_response('error', "Wrong code", status=status.HTTP_401_UNAUTHORIZED)
                    
            elif check_verification == 'success':
                user = get_object(CustomUser, id=validated_data['user_id'])
                user.verified_email = True
                user.save()
                return get_response('success', 'Verificated successfully!', status=status.HTTP_201_CREATED)
                    
        except:
            return get_response('error', 'Verificator never existed.', status=status.HTTP_400_BAD_REQUEST)
        
def reset_password(request, password):
    uidb64 = request.data['uid_64']
    token_key = request.data['token']

    user_id = urlsafe_base64_decode(uidb64).decode('utf-8')
    try:
        user = get_object(CustomUser, id=user_id)
    except:
        return get_response('error', 'User not found.', status=status.HTTP_401_UNAUTHORIZED)
    try:
        token_obj = get_object(Token, key=token_key)
    except:
        return get_response('error', 'Token not found.', status=status.HTTP_404_NOT_FOUND)
            
    if password:
        user.set_password(password)
        user.save()
        token_obj.delete()
    else:
        return get_response('error', "Passwords do not match.", status=status.HTTP_401_UNAUTHORIZED)
                
    return get_response('success', 'Password changed successfully!', {'note': 'You must relogin'}, status=status.HTTP_200_OK)