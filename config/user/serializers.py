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
from .services import get_object, change_data, create_user, create_object

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

        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        else:
            data.pop('password2')
        print(data)
        return data

    def create(self, validated_data):
        return create_user(validated_data)
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Проверяем существование пользователя с данным email
        user = get_object(CustomUser, email=email)

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
        user = get_object(CustomUser, id=data['user_id'], only_values=('email', 'verified_email'))
        return user
    
class CheckVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    user_id = serializers.CharField()
    
    def verificate(self, data):
        self.user_id = data['user_id']
        self.code = data['code']
        user = get_object(CustomUser, id=data['user_id'])
        verificator = get_object(Verificator, user=user)
        print(verificator)
        expired = verificator.is_expired()
        print(expired)
            # True if expired, else False
        if verificator:
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
        user = get_object(CustomUser, email=self.email)
        if user:
            user_uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8')) # encode 
            user_token = get_object(Token, user=user)
            return [user_uidb64, str(user_token), user.email]

            
            
class ResetPasswordSerializer(serializers.Serializer):
    uid_64 = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)
    password1 = serializers.CharField(max_length=255)
    password2 = serializers.CharField(max_length=255)
    
    def validate(self, data):
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
        fields = ['user_id', 'logo', 'banner', 'company_name', 'about',
                  'organization_type', 'industry_types', 'team_size',
                  'website', 'year_of_establishment', 'company_vision',
                  'map_location', 'phone_number']
        
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
            'social_links': {'required': False},
            
        }

    def update(self, instance, validated_data):
        fields_to_update = [
            'logo', 'banner', 'company_name', 'about', 'organization_type',
            'industry_types', 'team_size', 'website', 'year_of_establishment',
            'company_vision', 'map_location', 'phone_number'
        ]
        changed_instance = change_data(instance, fields_to_update, validated_data)
        social_links = validated_data.get('social_links')
        if social_links:
            for link in social_links:
                link_data = {
                    'employer': instance,
                    "social_network": link['social_media'],
                    "link": link['link'],
                    "frontend_id": link['id']
                }
                create_object(EmployerSocialLink, link_data)

        return changed_instance
    
    
class ChangeEmployerCompanyInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['logo', 'banner', 'company_name', 'about']
        
        extra_kwargs = {
            'logo': {'required': False},
            'banner': {'required': False},
            'company_name': {'required': False},
            'about' : {'required': False}
        }
        
    
    def update(self, instance, validated_data):
        fields_to_update = ['logo', 'banner', 'company_name', 'about']
        changed_instance = change_data(instance, fields_to_update, validated_data)

        return changed_instance
    
    
class ChangeEmployerFoundingInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['organization_type', 'industry_types', 'team_size', 'year_of_establishment', 'website', 'company_vision']
        
        extra_kwargs = {
            'organization_type': {'required': False},
            'industry_types': {'required': False},
            'team_size': {'required': False},
            'year_of_establishment': {'required': False},
            'website': {'required': False},
            'company_vision': {'required': False}
        }
        
    def change_founding(self, instance,  validated_data):
        fields_to_update = ['organization_type', 'industry_types', 'team_size', 'year_of_establishment', 'website', 'company_vision']
        changed_instance = change_data(instance, fields_to_update, validated_data)
        return changed_instance
    
class CreateEmployerSocialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmployerSocialLink
        fields = ['social_network', 'link']
        
    def create(self, instance, validated_data):
        fields_to_update = ['social_network', 'link']
        changed_instance = change_data(instance, fields_to_update, validated_data)
        return changed_instance
    
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
        fields_to_update = ['map_location', 'phone_number', 'email']
        changed_instance = change_data(instance, fields_to_update, data)
        return changed_instance
        


class ChangeCandidatePersonalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Candidate
        fields = ['profile_picture', 'full_name', 'headline', 'educations', 'website']
        extra_kwargs = {
            'user_id': {'required': True},
            'profile_picture': {'required': False},
            'full_name': {'required': False},
            'headline': {'required': False},
            'educations': {'required': False},
            'website': {'required': False}
        }

    def update(self, instance, validated_data):
        fields_to_update = ['profile_picture', 'full_name', 'headline', 'educations', 'website']
        data = change_data(instance, fields_to_update, validated_data)
        return data
            
        
class CreateResumeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ResumeFile
        fields = ['title', 'file']
        extra_kwargs = {
            'user_id': {'required': True},
        }
        
    def create(self, instance, data):
        return create_object(instance, data)
    
    

class ChangeResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['title', 'file']
        extra_kwargs = {
            'resume_id': {'required': True},
        }
    
    def change(self, instance, validated_data):
        fields_to_update = ['title', 'file']
        return change_data(instance, fields_to_update, validated_data)
        
        
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
            'user_id': {'required': True},
            'nationality': {'required': False},
            'date_of_birth': {'required': False},
            'gender': {'required': False},
            'marital_status': {'required': False},
            'biography': {'required': False}
        }
        
    def change_profile(self, candidate, data):
        fields_to_update = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'biography']
        return change_data(candidate, fields_to_update, data)
    
    
class CreateCandidateSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSocialLink
        fields = ['social_network', 'link']
        extra_kwargs = {
            'user_id': {'required': True},
        }
        
    def create_link(self, instance, data):
        user = get_object(CustomUser, id=data['user_id'])
        fields = {'user': user, 'social_network': data['social_network'], "link": data['link']}
        return create_object(instance, fields)
    
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
        fields = ['map_location', 'phone_number', "email"]
        extra_kwargs = {
            'user_id': {'required': True},
            'map_location': {'required': False},
            'phone_number': {'required': False},
            'email': {'required': False},
        }
        
    def change_settings(self, instance, data):
        fields_to_update = ['map_location', 'phone_number', 'email']
        return change_data(instance, fields_to_update, data)
    
class ChangeCandidateNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ["shortlist", "expire", "five_job_alerts", "profile_saved", "rejection"]
        extra_kwargs = {
            'user_id': {'required': True},
            "shortlist": {'required': False},
            "expire": {'required': False},
            "five_job_alerts": {'required': False},
            "profile_saved": {'required': False},
            "rejection": {'required': False},
            "profile_privacy": {'required': False},
            "resume_privacy": {'required': False},
        }
    def change_settings(self, instance, data):
        fields_to_update = ["shortlist", "expire", "five_job_alerts", "profile_saved", "rejection"]
        return change_data(instance, fields_to_update, data)
        
#"profile_privacy": {'required': False},
            #"resume_privacy": {'required': False},
            
class ChangeCandidatePrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ["profile_privacy", "resume_privacy"]
        extra_kwargs = {
            "profile_privacy": {'required': False},
            "resume_privacy": {'required': False},
        }
        
    def change_settings(self, instance, data):
        fields_to_update = ["profile_privacy", "resume_privacy"]
        return change_data(instance, fields_to_update, data)
    
    
class GetUserSerializer(serializers.Serializer):
    
    def find_user(self, token_key):
        user = get_object(CustomUser, auth_token=token_key)
        return user
        
        
class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    
    def delete_user(self, data):
        user = get_object(CustomUser, username=data['username'])
        if user:
            user.delete()
            return True
        
        
# class TestImageSerializer(serializers.Serializer):
#     image = serializers.ImageField()
#     user_file = serializers.FileField()
    
#     def check(self, data):
#         image = data['image']
#         user_file = data['user_file']
#         if image:
#             print(image)
#             return image