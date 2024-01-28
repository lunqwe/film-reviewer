from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Verificator
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone

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
    
class SendVerificationSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    
    def create(self, data):
        user = CustomUser.objects.filter(id=data['user_id'])[0]
        return user
    
class CheckVerificationSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    user_id = serializers.IntegerField()
    
    def validate(self, data):
        self.user_id = data['user_id']
        self.code = data['code']
        user = CustomUser.objects.filter(id=self.user_id)[0]
        if self.code and len(str(self.code)) == 6 and not user.verified_email:
            verificator = Verificator.objects.filter(user=user, code=self.code)[0]
            expired = verificator.is_expired()
            if verificator:
                if expired:
                    verificator.delete()
                    return 'expired'
                
                if verificator and not expired:
                    verificator.delete()
                    user.verified_email = True
                    return True
            else:
                return 'Something wrong'
            
            