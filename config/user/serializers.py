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
from .models import CustomUser, Verificator, Employer, Candidate, ResumeFile

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
    email = serializers.CharField()
    
    def validate(self, data):
        self.email = data['email']
        user = CustomUser.objects.get(email=self.email)
        if user:
            user_uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8')) # encode 
            user_token = Token.objects.get(user=user)
            return [user_uidb64, str(user_token), user.email]

            
            
class ResetPasswordSerializer(serializers.Serializer):
    uid_64 = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)
    password1 = serializers.CharField(max_length=255)
    password2 = serializers.CharField(max_length=255)
    
    def create(self, data):
        self.password1 = data['password1']
        self.password2 = data['password2']
        
        if self.password1 == self.password2:
            return self.password1
        
        
class SaveEmployerSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255)
    logo = serializers.ImageField(required=False, allow_null=True)
    banner = serializers.ImageField(required=False, allow_null=True)
    company_name = serializers.CharField(max_length=255)
    about = serializers.CharField(max_length=999)
    organization_type = serializers.CharField(max_length=255)
    industry_types = serializers.CharField(max_length=255)
    team_size = serializers.CharField(max_length=255)
    year_of_establishment = serializers.DateField()
    website = serializers.CharField(max_length=255)
    company_vision = serializers.CharField(max_length=999)
    map_location = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=30)
    email = serializers.EmailField()

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        employer_data = {
            'user': user,
            'company_name': validated_data['company_name'],
            'about': validated_data['about'],
            'organization_type': validated_data['organization_type'],
            'industry_types': validated_data['industry_types'],
            'team_size': validated_data['team_size'],
            'year_of_establishment': validated_data['year_of_establishment'],
            'website': validated_data['website'],
            'company_vision': validated_data['company_vision'],
            'map_location': validated_data['map_location'],
            'phone_number': validated_data['phone_number'],
            # 'email': validated_data['email'],
        }
        
        # Проверяем наличие логотипа
        if 'logo' in validated_data:
            employer_data['logo'] = validated_data['logo']

        # Проверяем наличие баннера
        if 'banner' in validated_data:
            employer_data['banner'] = validated_data['banner']

        employer = Employer.objects.create(**employer_data)
        return employer

class ChangeEmployerCompanyInfoSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    logo = serializers.ImageField(required=False, allow_null=True)
    banner = serializers.ImageField(required=False, allow_null=True)
    company_name = serializers.CharField(required=False, allow_null=True)
    about = serializers.CharField(required=False, allow_null=True)
    
    def change(self, data):
        user_id = data['user_id']
        user = CustomUser.objects.get(id=user_id)
        employer = Employer.objects.get(user=user)
        
        if 'logo' in data:
            employer.logo = data['logo']
            
        if 'banner' in data:
            employer.banner = data['banner']
        
        if 'company_name' in data:
            employer.company_name = data['company_name']
        
        if 'about' in data:
            employer.about = data['about']
        
        employer.save()
        
        return employer
    
    
class ChangeEmployerFoundingInfoSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    organization_type = serializers.CharField(required=False, allow_null=True)
    industry_types = serializers.CharField(required=False, allow_null=True)
    team_size = serializers.CharField(required=False, allow_null=True)
    year_of_establishment = serializers.DateField(required=False, allow_null=True)
    website = serializers.CharField(required=False, allow_null=True)
    company_vision = serializers.CharField(required=False, allow_null=True)
    
    def change_founding(self, data):
        user_id = data['user_id']
        user = CustomUser.objects.get(id=user_id)
        employer = Employer.objects.get(user=user)
        
        if 'organization_type' in data:
            employer.organization_type = data['organization_type']
        if 'industy_types' in data:
            employer.organization_type = data['industry_types']
        if 'team_size' in data:
            employer.team_size = data['team_size']
        if 'year_of_establishment' in data:
            employer.year_of_establishment = data['year_of_establishment']
        if 'website' in data:
            employer.website = data['website']
        if 'company_vision' in data:
            employer.company_vision = data['company_vision']
        
        employer.save()
        
        return employer



class ChangeCandidatePersonalSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False, allow_null=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    full_name = serializers.CharField(required=False, allow_null=True)
    headline = serializers.CharField(required=False, allow_null=True)
    education = serializers.CharField(required=False, allow_null=True)
    website = serializers.CharField(required=False, allow_null=True)
    
    def update(self, data):
        user_id = data['user_id']
        user = CustomUser.objects.get(id=user_id)
        candidate = Candidate.objects.get(user=user)
        
        if "profile_picture" in data:
            candidate.profile_picture = data['profile_picture']
            
        if "full_name" in data:
            candidate.full_name = data['full_name']
            
        if "headline" in data:
            candidate.headline = data['headline']
            
        if "education" in data:
            candidate.education = data['education']
            
        if 'website' in data:
            candidate.website = data['website']
            
        candidate.save()
        
        return candidate
            
        
class CreateResumeSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    title = serializers.CharField()
    file = serializers.FileField()
    
    
    
    def create(self, data):
        user_id = data['user_id']
        title = data['title']
        file = data['file']
        user = CustomUser.objects.get(id=user_id)
        candidate = Candidate.objects.get(user=user)
        
        if candidate:
            resume_obj = ResumeFile.objects.create(candidate=candidate, title=title, file=file)
            
            return resume_obj.id

class ChangeResumeSerializer(serializers.Serializer):
    resume_id = serializers.CharField()
    file = serializers.FileField()
    
    def change(self, data):
        resume_id = data['resume_id']
        file = data['file']
        
        resume = ResumeFile.objects.get(id=resume_id)
        
        if resume:
            resume.file.delete()
            resume.file = file
            resume.save()
            
            return resume
        
        
class DeleteResumeSerializer(serializers.Serializer):
    resume_id = serializers.CharField()
    
    def delete_resume(self, data):
        resume_id = data['resume_id']
        resume = ResumeFile.objects.get(id=resume_id)
        
        if resume:
            resume.delete()
            
            return True
        
        
        