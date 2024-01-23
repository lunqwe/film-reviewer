from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser
# Create your views here.

User = get_user_model()

from .serializers import UserSerializer, LoginSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Перевірка наявності користувача за ім'ям або поштою
        username_exists = CustomUser.objects.filter(username=serializer.validated_data['username']).exists()
        email_exists = CustomUser.objects.filter(email=serializer.validated_data['email']).exists()

        if username_exists:
            # Користувач з таким ім'ям або поштою вже існує, повертаємо відповідь про конфлікт
            return Response({'error': 'User with this username already exists.'}, status=status.HTTP_409_CONFLICT)
        
        if email_exists:
            return Response({'error': 'Email is already in use.'}, status=status.HTTP_409_CONFLICT)

        # Ізвлекаємо пароль з серіалізатора
        password = serializer.validated_data.pop('password')

        # Створюємо користувача без password1 та password2
        user = CustomUser.objects.create(**serializer.validated_data)

        # Встановлюємо пароль користувача
        user.set_password(password)
        user.save()

        return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
    

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        print(user)

        if user:
            # Если пользователь аутентифицирован успешно, создаем или получаем токен
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            # Если аутентификация не удалась, возвращаем ошибку
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
        
