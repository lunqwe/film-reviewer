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
from .models import CustomUser, Verificator, Employer, Candidate, ResumeFile, EmployerSocialLink, CandidateSocialLink

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
        
        
class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    current_password = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    
    def change(self, user, data):
        password1 = data['password1']
        password2 = data['password2']
        
        if password1 == password2:
            user.set_password(password1)
            user.save()
            return user
        
        
        
        
class SaveEmployerSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Employer
        fields = ['user_id', 'logo', 'banner', 'company_name', 'about', 'organization_type', 'industry_types', 'team_size', 'website', 'year_of_establishment', 'company_vision', 'map_location', 'phone_number']
        
        extra_kwargs = {
            'logo': {'required': False},
            'banner': {'required': False},
            'company_name': {'required': False},
            'about': {'required': False},
            'organization_type': {'required': False},
            'industry_types': {'required': False},
            'team_size': {'required': False},
            'website': {'required': False},
            'year_of_establishment': {'required': False},
            'company_vision': {'required': False},
            'map_location': {'required': False},
            'phone_number': {'required': False},
            
        }

    def update(self, instance, validated_data):
        instance.logo = validated_data.get('logo', instance.logo)
        instance.banner = validated_data.get('banner', instance.banner)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.about = validated_data.get('about', instance.about)
        instance.organization_type = validated_data.get('organization_type', instance.organization_type)
        instance.industry_types = validated_data.get('industry_types', instance.industry_types)
        instance.team_size = validated_data.get('team_size', instance.team_size)
        instance.website = validated_data.get('website', instance.website)
        instance.year_of_establishment = validated_data.get('year_of_establishment', instance.year_of_establishment)
        instance.company_vision = validated_data.get('company_vision', instance.company_vision)
        instance.map_location = validated_data.get('map_location', instance.map_location)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        
        instance.save()
        return instance
    
    
class ChangeEmployerCompanyInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['user_id', 'logo', 'banner', 'company_name', 'about']
        
        extra_kwargs = {
            'logo': {'required': False},
            'banner': {'required': False},
            'company_name': {'required': False},
            'about' : {'required': False}
        }
        
    
    def update(self, instance, data):
        
        instance.logo = data.get('logo', instance.logo)
        instance.banner = data.get('banner', instance.banner)
        instance.company_name = data.get('company_name', instance.company_name)
        instance.about = data.get('about', instance.about)
        
        instance.save()
        return instance
    
    
class ChangeEmployerFoundingInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['user_id', 'organization_type', 'industry_types', 'team_size', 'year_of_establishment', 'website', 'company_vision']
        
        extra_kwargs = {
            'organization_type': {'required': False},
            'industry_types': {'required': False},
            'team_size': {'required': False},
            'year_of_establishment': {'required': False},
            'website': {'required': False},
            'company_vision': {'required': False}
        }
        
    def change_founding(self, instance,  data):
        instance.organization_type = data.get('organization_type', instance.organization_type)
        instance.industry_types = data.get('industry_types', instance.industry_types)
        instance.team_size = data.get('team_size', instance.team_size)
        instance.year_of_establishment = data.get('year_of_establishment', instance.year_of_establishment)
        instance.website = data.get('website', instance.website)
        instance.company_vision = data.get('company_vision', instance.company_vision)
        
        instance.save()
        return instance
    
class CreateEmployerSocialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmployerSocialLink
        fields = ['social_network', 'link']
        
    def create(self, instance, data):
        instance.social_network = data.get('social_network', instance.social_network)
        instance.link = data.get('link', instance.link)
        
        instance.save()
        return instance
    
class ChangeEmployerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['map_location', 'phone_number', 'email']
        extra_kwargs = {
            'map_location': {'required': False},
            'phone_number': {'required': False},
            'email': {'required': False}
        }
        
    def change(self, instance, data):
        instance.map_location = data.get('map_location', instance.map_location)
        instance.phone_number = data.get('phone_number', instance.phone_number)
        instance.email = data.get('email', instance.email)
        
        instance.save()
        return instance
        


class ChangeCandidatePersonalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Candidate
        fields = ['user_id', 'profile_picture', 'full_name', 'headline', 'educations', 'website']
        extra_kwargs = {
            'user_id': {'required': False},
            'profile_picture': {'required': False},
            'full_name': {'required': False},
            'headline': {'required': False},
            'educations': {'required': False},
            'website': {'required': False}
        }

    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.headline = validated_data.get('headline', instance.headline)
        instance.educations = validated_data.get('educations', instance.educations)
        instance.website = validated_data.get('website', instance.website)
        instance.save()
        return instance
            
        
class CreateResumeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ResumeFile
        fields = ['title', 'file']
        
    def create(self, instance, data):
        instance.title = data.get('title', instance.title)
        instance.file = data.get('file', instance.file)
        
        instance.save()
        return instance
    
    

class ChangeResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['title', 'file']
    
    def change(self, instance, data):
        instance.title = data.get('title', instance.title)
        instance.file = data.get('file', instance.file)
        
        instance.save()
        return instance
        
        
class DeleteResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['id']
    
    def delete_resume(self, instance):
        instance.delete()
        return True
        
        
    
class ChangeCandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'biography']
        
        extra_kwargs = {
            'nationality': {'required': False},
            'date_of_birth': {'required': False},
            'gender': {'required': False},
            'marital_status': {'required': False},
            'biography': {'required': False}
        }
        
    def change_profile(self, candidate, data):
        candidate.nationality = data.get('nationality', candidate.nationality)
        candidate.date_of_birth = data.get('date_of_birth', candidate.date_of_birth)
        candidate.gender = data.get('gender', candidate.gender)
        candidate.marital_status = data.get('marital_status', candidate.marital_status)
        candidate.biography = data.get('biography', candidate.biography)
        
        candidate.save()
        return candidate
    
    
class CreateCandidateSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSocialLink
        fields = ['social_network', 'link']
        
    def create_link(self, instance, data):
        instance.social_network = data.get('social_network', instance.social_network)
        instance.link = data.get('link', instance.link)
        
        instance.save()
        return instance
    
class DeleteCandidateSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSocialLink
        fields = ['id']
    
    def delete_link(self, instance):
        instance.delete()
        return True
    
class ChangeCandidateAccountSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['map_location', 'phone_number', 'email', "shortlist", "expire", "five_job_alerts", "profile_saved", "rejection", "profile_privacy", "resume_privacy"]
        extra_kwargs = {
            'map_location': {'required': False},
            'phone_number': {'required': False},
            'email': {'required': False},
            "shortlist": {'required': False},
            "expire": {'required': False},
            "five_job_alerts": {'required': False},
            "profile_saved": {'required': False},
            "rejection": {'required': False},
            "profile_privacy": {'required': False},
            "resume_privacy": {'required': False},
        }
        
    def change_settings(self, instance, data):
        instance.map_location = data.get('map_location', instance.map_location)
        instance.phone_number = data.get('phone_number', instance.phone_number)
        instance.email = data.get('email', instance.email)
        instance.shortlist = data.get('shortlist', instance.shortlist)
        instance.expire = data.get('expire', instance.expire)
        instance.five_job_alerts = data.get('five_job_alerts', instance.five_job_alerts)
        instance.profile_saved = data.get('profile_saved', instance.profile_saved)
        instance.rejection = data.get('rejection', instance.rejection)
        instance.profile_privaсy = data.get('profile_privacy', instance.profile_privacy)
        instance.resume_privacy = data.get('resume_privacy', instance.resume_privacy)
        
        instance.save()
        return instance
    
class GetUserSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def find_user(self, data):
        token = Token.objects.get(key=data['token'])
        return token.user
        
        
class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    
    def delete_user(self, data):
        user = CustomUser.objects.get(username=data['username'])
        if user:
            user.delete()
            return True
        