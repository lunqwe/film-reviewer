from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser
from rest_framework import serializers
from django.core.mail import EmailMessage
import random
# Create your views here.

User = get_user_model()

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
                user.verification_code = str(generated_code)
                user.save()
                email = EmailMessage('Jobpilot email verification', str(generated_code), from_email='jobpilot@ukr.net', to=[user.email])
                email.send()
            
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
        
        if check_verification:
            return Response({'status': 'success', 'detail': 'Verificated successfully!'}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({'status': 'error', 'detail': 'Wrong code.'}, status=status.HTTP_400_BAD_REQUEST)