from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser
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
        
        # Создаем пользователя
        user = User.objects.create(**validated_data)

        # Устанавливаем пароль
        user.set_password(password)
        user.save()

        return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    