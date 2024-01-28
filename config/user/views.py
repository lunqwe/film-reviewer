from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser, Verificator
from rest_framework import serializers
from django.core.mail import EmailMessage
import os
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import random
from decouple import AutoConfig

User = get_user_model()
config = AutoConfig()

from .serializers import UserSerializer, LoginSerializer, SendVerificationSerializer, CheckVerificationSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.pop('password')

            user = CustomUser.objects.create(**serializer.validated_data)
            print(user)
            
            user.set_password(password)
            user.save()

            return Response({'status': "success",  'detail': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            errors = e.detail
            
            email_error = errors.get('email', [])[0] if errors.get('email') else None
            username_error = errors.get('username', [])[0] if errors.get('username') else None
            password_error = errors.get('non_field_errors', [])[0] if errors.get('non_field_errors') else None
            
            response_data = {'status': 'error'}
            
            if email_error:
                response_data['email'] = email_error
            
            if username_error:
                response_data['username'] = username_error
                
            if password_error:
                response_data['password'] = password_error
            
            
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            # Если валидация успешна, вернуть успешный ответ
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            # Обработка ошибок валидации
            errors = e.detail
            error_detail = errors.get('non_field_errors', [])[0] if errors.get('non_field_errors') else None
            print(error_detail)
            return Response({'status': 'error', 'detail': error_detail}, status=status.HTTP_400_BAD_REQUEST)
            
class VerifyEmailView(generics.CreateAPIView):
    serializer_class = SendVerificationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = serializer.create(request.data)
        check_verified = user.verified_email
        
        if user:
            if not check_verified:
                generated_code = random.randint(100000,1000000)
                verificator = Verificator.objects.get(user=user)
                print(generated_code)
                verificator.code = str(generated_code)
                verificator.save()
                sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY') )
                message = Mail(
                    from_email=From('jobpilot@ukr.net', 'Jobpilot'),
                    to_emails=To(user.email),
                    subject='Jobpilot email verification',
                    plain_text_content=str(generated_code)
                )

                response = sg.send(message)
                print(response)
                
             
                return Response({'status': 'success', 'detail': 'Verification message sent!'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 'error', 'detail': 'User is already verified or server stopped connection to smtp server.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'detail': 'Failed to get user email.'}, status=status.HTTP_400_BAD_REQUEST)

class CheckVerificationView(generics.CreateAPIView):
    serializer_class = CheckVerificationSerializer
    
    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        check_verification = serializer.validate(request.data)
        user = CustomUser.objects.filter(id=request.data['user_id'])[0]
        
        if user.verified_email:
            return Response({'status': 'error', 'detail': 'User email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        if check_verification == 'expired':
            return Response({'status':'error', 'detail': 'Verification code expired.'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        elif check_verification == 'wrong_code':
            return Response({'status': 'error', 'detail': "Verificator never existed."}, status=status.HTTP_401_UNAUTHORIZED)
        
        elif check_verification:
            return Response({'status': 'success', 'detail': 'Verificated successfully!'}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({'status': 'error', 'detail': 'Verificator never existed.'}, status=status.HTTP_400_BAD_REQUEST)