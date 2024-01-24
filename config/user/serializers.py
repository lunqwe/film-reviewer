from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'password', 'password2', 'status']

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        # Проверяем, совпадают ли пароли
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        else:
            data.pop('password2')
        print(data)
        return data

    def create(self, validated_data):
        # Используем только первый введенный пароль
        print(validated_data)
        password = validated_data.pop('password2')
        print(validated_data)
        
        user = User.objects.create(**validated_data)

        user.set_password(password)
        user.save()

        print(user)
        return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Проверяем существование пользователя с данным email
        user = User.objects.filter(email=email).first()

        if user:
            # Проверяем валидность пароля
            if authenticate(request=self.context.get('request'), email=email, password=password):
                # Если пароль валиден, создаем или получаем токен
                token, created = Token.objects.get_or_create(user=user)
                return {'status': 'success', 'token': token.key}
            else:
                # Если пароль неверен
                raise serializers.ValidationError('Invalid password')
        else:
            # Если пользователя с таким email не существует
            raise serializers.ValidationError('Email not registered')
    

    