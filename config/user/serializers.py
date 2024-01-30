from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .models import CustomUser, Verificator, Employer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
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
        user = CustomUser.objects.filter(email=email).first()

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
    code = serializers.CharField(max_length=6)
    user_id = serializers.IntegerField()
    
    def validate(self, data):
        self.user_id = data['user_id']
        self.code = data['code']
        user = CustomUser.objects.get(id=self.user_id)
        if self.code and len(self.code) == 6 and not user.verified_email:
            verificator = Verificator.objects.get(user=user)
            expired = verificator.is_expired()
            # True if expired, else False
            if not expired:
                if self.code == verificator.code:
                    user.verified_email = True
                    verificator.delete()
                    return 'success'
                else:
                    return 'wrong_code'
            else:
                verificator.delete()
                return 'expired'
            
class ResetPasswordRequestSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    
    def validate(self, data):
        self.user_id = data['user_id']
        user = CustomUser.objects.get(id=self.user_id)
        if user:
            user_uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8')) # encode 
            user_token = Token.objects.get(user=user)
            return [user_uidb64, str(user_token)]

            
            
class ResetPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(max_length=255)
    password2 = serializers.CharField(max_length=255)
    
    def create(self, data):
        self.password1 = data['password1']
        self.password2 = data['password2']
        
        if self.password1 == self.password2:
            return self.password1
        
        
class SaveEmployerSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255)
    # logo = serializers.ImageField(blank=True, null=True)
    # banner = models.ImageField(blank=True, null=True)
    company_name = serializers.CharField(max_length=255)
    about = serializers.TextField(blank=True, null=True)
    
    organization_type = serializers.CharField(max_length=255, default='0')
    industry_types = serializers.CharField(max_length=255, default='0')
    team_size = serializers.CharField(max_length=255, default='0')
    year_of_establishment = serializers.DateField(blank=True, null=True)
    website = serializers.CharField(max_length=255)
    company_vision = serializers.TextField(blank=True, null=True)
    
    map_location = serializers.CharField(max_length=255, blank=True, null=True)
    phone_number = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    
    def create(self, data):
        self.user_id = data.get('user_id')
        self.company_name = data.get('company_name')
        self.about = data.get('about')
        self.organization_type = data.get('organization_type')
        self.industry_types = data.get('industry_types')
        self.team_size = data.get('team_size')
        self.year_of_establishment = data.get('year_of_establishment')
        self.website = data.get('website')
        self.company_vision = data.get('company_vision')
        self.map_location = data.get('map_location')
        self.phone_number = data.get('phone_number')
        self.email = data.get('email')
        
        user = CustomUser.objects.get(id=self.user_id)
        
        employer = Employer.objects.create(user=user,
                                           company_name=self.company_name,
                                           about=self.about,
                                           organization_type=self.organization_type,
                                           industry = self.industry_types,
                                           team_size = self.team_size,
                                           website = self.website,
                                           year_of_establishment = self.year_of_establishment,
                                           company_vision= self.company_vision,
                                           map_location = self.map_location,
                                           phone_number = self.phone_number,
                                           email = self.email)
        
        return employer

# class DeleteDaynSerializer(serializers.Serializer):
#     dayn = serializers.CharField()
    
#     def create(self, data):
#         user = CustomUser.objects.get(username=data['username'])
        
#         if user:
#             return user
    