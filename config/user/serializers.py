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
        
        username_exists = CustomUser.objects.filter(username=validated_data['username']).exists()
        email_exists = CustomUser.objects.filter(email=validated_data['email']).exists()
        error_check = False
        
        if username_exists:
            raise serializers.ValidationError('Username is already taken.')
            error_check = True
        
        if email_exists:
            raise serializers.ValidationError('Email is already registered.')
            error_check
        
        if not error_check:
            user = User.objects.create(**validated_data)

            # Устанавливаем пароль
            user.set_password(password)
            user.save()

            return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    