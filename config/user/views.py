from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from decouple import AutoConfig
import os
import random
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
from .serializers import *
from .models import CustomUser, Verificator, Candidate, Employer, ResumeFile
from common.services import *
from .services import *
from django.http import QueryDict



User = get_user_model()
config = AutoConfig()


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return create_user(request.data)
        
        except serializers.ValidationError as e:
            errors = e.detail
            
            email_error = errors.get('email', [])[0] if errors.get('email') else None
            username_error = errors.get('username', [])[0] if errors.get('username') else None
            password_error = errors.get('non_field_errors', [])[0] if errors.get('non_field_errors') else None
            
            response_data = {'status': 'error'}
            
            if email_error:
                response_data['email'] = email_error
            
            if username_error:
                response_data['username'] = username_error
                
            if password_error:
                response_data['password'] = password_error
            
            print(e)
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            # Если валидация успешна, вернуть успешный ответ
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return error_detail(e)
        
            
class VerifyEmailView(generics.CreateAPIView):
    serializer_class = SendVerificationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.create(request.data)
            check_verified = user.verified_email
            
            if user:
                if not check_verified:
                    return send_verification(user)
                else:
                    return get_response('error', "User is already verified.", status=status.HTTP_400_BAD_REQUEST)
            else:
                return get_response('error', 'Failed to get user email.', status=status.HTTP_400_BAD_REQUEST)
            
        except serializers.ValidationError as e:
            return error_detail(e)
        

class CheckVerificationView(generics.CreateAPIView):
    serializer_class = CheckVerificationSerializer
    
    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return check_verification(request.data)
            
        except serializers.ValidationError as e:
            return error_detail(e)
        
            
class SendResetPassView(generics.CreateAPIView):
    serializer_class = ResetPasswordRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validate(request.data)
            
            reset_link = f'http://localhost:3000/reset-password/{user_data[0]}/{user_data[1]}'
            if user_data:
                mail = send_email(user_email=user_data[2], subject='Jobpilot reset password request', email_content=reset_link)
                if mail:
                    return get_response('success', 'Password reset link sent.', {'user_id': user_data[0], 'token': user_data[1]}, status=status.HTTP_200_OK)
                else:
                    return get_response('error', "Error sending email. (401 Unauthorized)", status=status.HTTP_401_UNAUTHORIZED)
            else:
                return get_response('error', 'Error creating password reset link: user not found.', status=status.HTTP_400_BAD_REQUEST)
            
        except serializers.ValidationError as e:
            return error_detail(e)
        
        
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            password = serializer.validate(request.data)
            return reset_password(request, password)
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangePasswordView(generics.CreateAPIView):
    serializer_class = ChangePasswordSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            current_password = request.data['current_password']
            user = get_object(CustomUser, id=request.data['user_id'])
            
            if user.check_password(current_password):
                return change_password(user, request.data)
            else:
                return get_response('error', "Wrong current password.", status=status.HTTP_401_UNAUTHORIZED) 
            
        except serializers.ValidationError as e:
            return error_detail(e)
        
class SaveEmployerImagesView(generics.CreateAPIView):
    serializer_class = SaveEmployerImagesSerializer
    
    def validate(self, data):
        query_dict = QueryDict('', mutable=True)
        for key, value in data.items():
            if key == 'logo' and isinstance(value, str):
                print(key, value)
                continue
            elif key == 'banner' and isinstance(value, str):
                print(key, value)
                continue
            query_dict.appendlist(key, value)
        return query_dict
        
    
    def create(self, request):
        validated_data = self.validate(request.data)
        print(validated_data.keys())
        serializer = self.get_serializer(data=validated_data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer_obj = get_obj_by_user_id(Employer, validated_data['user_id'])
            employer = serializer.update(employer_obj, validated_data)
            
            if not employer:
                return get_response('error', "Error updating employer.")
            
            return get_response("success", "Employer images changed successfully!", {'logo': employer.logo.url, 'banner': employer.banner.url}, status=status.HTTP_202_ACCEPTED)
        
        except serializers.ValidationError as e:
            return error_detail(e)



class SaveEmployerDataView(generics.CreateAPIView):
    serializer_class = SaveEmployerDataSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer = get_obj_by_user_id(Employer, request.data['user_id'])
            employer_created = serializer.update(employer, request.data)
            
            if not employer_created:
                return get_response('error', "Error creating employer.", status=status.HTTP_400_UNAUTHORIZED)
            
            return get_response("success", "Employer created successfully!", status=status.HTTP_202_ACCEPTED)
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangeEmployerCompanyInfoView(generics.CreateAPIView):
    serializer_class = ChangeEmployerCompanyInfoSerializer
    
    def validate(self, data):
        query_dict = QueryDict('', mutable=True)
        for key, value in data.items():
            if (key == 'logo' or key == 'banner') and isinstance(value, str):
                print(key, value)
                continue
            query_dict.appendlist(key, value)
        return query_dict
    
    def create(self, request):
        validated_data = self.validate(request.data)
        serializer = self.get_serializer(data=validated_data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer = get_obj_by_user_id(Employer, request.data['user_id'])
            employer_changed = serializer.update(employer, request.data)
            
            if not employer_changed:
                return get_response('error', 'Error changing employer data.')
            
            return get_response("success", 'Employer company info changed successfully!')
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
    
class ChangeEmployerFoundingInfoView(generics.CreateAPIView):
    serializer_class = ChangeEmployerFoundingInfoSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer = get_obj_by_user_id(Employer, request.data['user_id'])
            employer_changed = serializer.change_founding(employer, request.data)
            
            if not employer_changed:
                return get_response('error', 'Failed to change employer`s founding info.')
            
            return get_response("success", "Employer founding info changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class EmployerSocialLinksView(generics.CreateAPIView):
    serializer_class = EmployerSocialLinksSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer = get_obj_by_user_id(Employer, request.data['user_id'])
            links_created = serializer.change_links(employer, request.data)
            
            if not links_created:
                return get_response('error', 'Error creating links model')
            
            return get_response('success', "Links added successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)


class ChangeEmployerContactView(generics.CreateAPIView):
    serializer_class = ChangeEmployerContactSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            employer = get_obj_by_user_id(Employer, request.data['user_id'])
            employer_changed = serializer.change(employer, request.data)
            
            if not employer_changed:
                return get_response('error', 'Error changing employer contacts')
            
            return get_response('success', "Employer contacts changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
        

class ChangeCandidatePersonalView(generics.CreateAPIView):
    serializer_class = ChangeCandidatePersonalSerializer
    
    def validate(self, data):
        query_dict = QueryDict('', mutable=True)
        for key, value in data.items():
            if key == 'profile_picture' and isinstance(value, str):
                print(key, value)
                continue
            query_dict.appendlist(key, value)
        return query_dict
        
    
    def create(self, request):
        validated_data = self.validate(request.data)
        serializer = self.get_serializer(data=validated_data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate_obj = get_obj_by_user_id(Candidate, validated_data['user_id'])
            candidate = serializer.update(candidate_obj, validated_data)
            
            if not candidate:
                return get_response('error', "Error updating candidate.")
            
            return get_response("success", "Candidate info changed successfully!", {'profile_picture': candidate.profile_picture.url}, status=status.HTTP_202_ACCEPTED)
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
        
class CreateResumeView(generics.CreateAPIView):
    serializer_class = CreateResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            new_data = {'title': request.data['title'], 'file': request.data['file']}
            resume = serializer.create(candidate, new_data)
            
            if not resume:
                return get_response('error', "Error creating resume", status=status.HTTP_400_BAD_REQUEST)
            
            return get_response("success", "Resume created successfully!", {'resume_id': resume.id, 'title': resume.title, 'file': resume.file.url}, status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangeResumeView(generics.CreateAPIView):
    serializer_class = ChangeResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            resume = get_object(ResumeFile, id=request.data['resume_id'])
            resume_changed = serializer.change(resume, request.data)
            
            if not resume_changed:
                return get_response('error', 'Error changing resume', status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', 'Resume file changed successfully!', {'resume_id': resume.id, 'resume_title': resume.title, 'file_url': resume.file.url}, status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            return error_detail(e)
    

class DeleteResumeView(generics.CreateAPIView):
    serializer_class = DeleteResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            resume = get_object(ResumeFile, id=request.data['resume_id'])
            resume_deleted = serializer.delete_resume(resume)
            if not resume_deleted:
                return get_response("error", "Error deleting resume", status=status.HTTP_400_BAD_REQUEST)
            
            return get_response("success", "Resume deleted successfully!", status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class ChangeCandidateProfileView(generics.CreateAPIView):
    serializer_class = ChangeCandidateProfileSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            change_personal = serializer.change_profile(candidate, request.data)
            
            if not change_personal:
                return get_response('error', "Failed to change profile candidate data.")
            
            return get_response('success', 'Candidate`s profile data changed successfully!', status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class CandidateSocialLinksView(generics.CreateAPIView):
    serializer_class = CandidateSocialLinksSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            changed_links = serializer.change_links(candidate, request.data)
            
            if not changed_links:
                return get_response('error', "Error creating candidate social link", status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', 'Candidate social network links changed successfully!', status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            return error_detail(e)
    

    
class ChangeCandidateAccountSettingsView(generics.CreateAPIView):
    serializer_class = ChangeCandidateAccountSettingsSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate settings', status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', "Candidate settings changed successfully!", status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class ChangeCandidateNotificationsAndAlertsView(generics.CreateAPIView):
    serializer_class = ChangeCandidateNotificationsSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate notifications', status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', "Candidate notifications changed successfully!", status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return error_detail(e)
            
class ChangeCandidatePrivacyView(generics.CreateAPIView):
    serializer_class = ChangeCandidatePrivacySerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            candidate = get_obj_by_user_id(Candidate, request.data['user_id'])
            print(request.data)
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate privacy', status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', "Candidate privacy changed successfully!", status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return error_detail(e)


class GetUserView(generics.CreateAPIView):
    serializer_class = GetUserSerializer
    
    def get(self, request, token):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.find_user(token)
            
            if not user:
                raise NotFound("User not found.")

            return get_user(user)
            
        except serializers.ValidationError as e:
            return error_detail(e)
    
    
class DeleteUserView(generics.CreateAPIView):
    serializer_class = DeleteUserSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            delete_user = serializer.delete_user(request.data)
            
            if not delete_user:
                return get_response('error', "Error deleting user", status=status.HTTP_400_BAD_REQUEST)
            
            return get_response('success', "User deleted successfully!", status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            return error_detail(e)
        

# class TestImageView(generics.CreateAPIView):
#     serializer_class = TestImageSerializer
    
#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         check_valid = serializer.check(request.data)
        
#         if not check_valid:
#             return get_response('error', 'watafak wrong data', status=status.HTTP_306_RESERVED)
        
#         return get_response('vse zaebok', '123', status=status.HTTP_200_OK)
        