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
from .services import get_object, change_data, create_user, create_object

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'full_name', 'password', 'password2', 'status']
        extra_kwargs = {
            "user_id": {'required': True}
        }
        
        
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

        # Проверяем существование пользователя
        try:
            user = get_object(CustomUser, email=email)

            if user:
                # Проверяем валидность пароля
                if authenticate(request=self.context.get('request'), email=email, password=password):
                    # Если пароль валиден, создаем или получаем токен
                    token, created = Token.objects.get_or_create(user=user)
                    return {'status': 'success', 'token': token.key}
                else:
                    # Если пароль неверен
                    return {'status': 'error', 'detail': "Invalid password"}
        except Exception as e:
            print(e)
            # Если пользователя с таким email не существует
            return {'status': 'error', 'detail': "Email is not registered."}
    
class SendVerificationSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    
    def create(self, data):
        user = get_object(CustomUser, id=data['user_id'])
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
        fields = ['logo', 'banner', 'company_name', 'about',
                  'organization_type', 'industry_types', 'team_size',
                  'website', 'year_of_establishment', 'company_vision',
                  'map_location', 'phone_number', 'links']
        
        extra_kwargs = {
            "user_id": {'required': True}
        }

    def update(self, instance, validated_data):
        fields_to_update = [
            'logo', 'banner', 'company_name', 'about', 'organization_type',
            'industry_types', 'team_size', 'website', 'year_of_establishment',
            'company_vision', 'map_location', 'phone_number', 'links'
        ]
        changed_instance = change_data(instance, fields_to_update, validated_data)
        social_links = validated_data.get('links')
        if social_links:
            instance.links = social_links

        return changed_instance
    
    
class ChangeEmployerCompanyInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['logo', 'banner', 'company_name', 'about']
        
        extra_kwargs = {
            "user_id": {'required': True}
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
            "user_id": {'required': True}
        }
        
    def change_founding(self, instance,  validated_data):
        fields_to_update = ['organization_type', 'industry_types', 'team_size', 'year_of_establishment', 'website', 'company_vision']
        changed_instance = change_data(instance, fields_to_update, validated_data)
        return changed_instance
    
class EmployerSocialLinksSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employer
        fields = ['links']
        
    def change_links(self, employer, validated_data):
        fields_to_update = ['links']
        changed_instance = change_data(employer, fields_to_update, validated_data)
        return changed_instance
    
class ChangeEmployerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['map_location', 'phone_number', 'email']
        extra_kwargs = {
            "user_id": {'required': True},

        }
        
    def change(self, instance, data):
        fields_to_update = ['map_location', 'phone_number', 'email']
        changed_instance = change_data(instance, fields_to_update, data)
        return changed_instance
        


class ChangeCandidatePersonalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Candidate
        fields = ['profile_picture', 'full_name', 'headline', 'educations','experiences', 'website']
        extra_kwargs = {
            'user_id': {'required': True}
        }

    def update(self, instance, validated_data):
        fields_to_update = ['profile_picture', 'full_name', 'headline', 'educations', 'experiences', 'website']
        data = change_data(instance, fields_to_update, validated_data)
        return data
            
        
class CreateResumeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ResumeFile
        fields = ['title', 'file', 'size']
        
    def create(self, instance, data):
        resume = ResumeFile.objects.create(candidate=instance, **data)
        return resume
        
    
    

class ChangeResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['file']
        extra_kwargs = {
            'resume_id': {'required': True},
        }
    
    def change(self, instance, validated_data):
        fields_to_update = ['title', 'file']
        instance.file.delete()
        return change_data(instance, fields_to_update, validated_data)
        
        
class DeleteResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['id']
        extra_kwargs = {
            'id': {'required': False},
            'resume_id': {'required': True}
        }
    
    def delete_resume(self, instance):
        instance.file.delete()
        instance.delete()
        return True
        
        
    
class ChangeCandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'biography']
        
        extra_kwargs = {
            'user_id': {'required': True},
        }
        
    def change_profile(self, candidate, data):
        fields_to_update = ['nationality', 'date_of_birth', 'gender', 'marital_status', 'biography']
        return change_data(candidate, fields_to_update, data)
    
    
class CandidateSocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['links']
        extra_kwargs = {
            'user_id': {'required': True},
        }
        
    def change_links(self, candidate, data):
        fields_to_update = ['links']
        return change_data(candidate, fields_to_update, data)
    
    
class ChangeCandidateAccountSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['map_location', 'phone_number', "email"]
        extra_kwargs = {
            'user_id': {'required': True},
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
            #add job alerts here
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