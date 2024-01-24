from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser
from rest_framework import serializers
# Create your views here.

User = get_user_model()

from .serializers import UserSerializer, LoginSerializer

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
            
