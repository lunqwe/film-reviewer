from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from decouple import AutoConfig
import os
import random
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
from .serializers import *
from .models import CustomUser, Verificator, Candidate, Employer, ResumeFile, EmployerSocialLink



User = get_user_model()
config = AutoConfig()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.pop('password')
            user_type = request.data['status']

            user = CustomUser.objects.create(**serializer.validated_data)
            print(user)
            user.set_password(password)
            user.save()
            
            if user_type:
                if user_type == 'candidate':
                    candidate = Candidate.objects.create(user=user)
                
                elif user_type == 'employer':
                    employer = Employer.objects.create(user=user)
                    
                else:
                    return Response({'status': 'error', 'detail': 'Wrong user status.'}, status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                return Response({'status': 'error', 'detail': 'User status specification required.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': "success",  'detail': 'User created successfully!', 'id': user.id}, status=status.HTTP_201_CREATED)
        
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
            # Обработка ошибок валидации
            errors = e.detail
            error_detail = errors.get('non_field_errors', [])[0] if errors.get('non_field_errors') else None
            print(error_detail)
            return Response({'status': 'error', 'detail': error_detail}, status=status.HTTP_400_BAD_REQUEST)
            
class VerifyEmailView(generics.CreateAPIView):
    serializer_class = SendVerificationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = serializer.create(request.data)
        check_verified = user.verified_email
        
        print(request.data)
        
        if user:
            if not check_verified:
                generated_code = random.randint(100000,1000000)
                verificator = Verificator.objects.create(user=user)
                print(generated_code)
                verificator.code = str(generated_code)
                verificator.save()
                sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY') )
                message = Mail(
                    from_email=From('jobpilot@ukr.net', 'Jobpilot'),
                    to_emails=To(user.email),
                    subject='Jobpilot email verification',
                    plain_text_content=str(generated_code)
                )

                response = sg.send(message)
                print(response)
                
             
                return Response({'status': 'success', 'detail': 'Verification message sent!'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 'error', 'detail': 'User is already verified or server stopped connection to smtp server.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'detail': 'Failed to get user email.'}, status=status.HTTP_400_BAD_REQUEST)

class CheckVerificationView(generics.CreateAPIView):
    serializer_class = CheckVerificationSerializer
    
    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        check_verification = serializer.validate(request.data)
        user = CustomUser.objects.filter(id=request.data['user_id'])[0]
        
        if user.verified_email:
            return Response({'status': 'error', 'detail': 'User email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        if check_verification == 'expired':
            return Response({'status':'error', 'detail': 'Verification code expired.'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        elif check_verification == 'wrong_code':
            return Response({'status': 'error', 'detail': "Verificator never existed."}, status=status.HTTP_401_UNAUTHORIZED)
        
        elif check_verification == 'success':
            return Response({'status': 'success', 'detail': 'Verificated successfully!'}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({'status': 'error', 'detail': 'Verificator never existed.'}, status=status.HTTP_400_BAD_REQUEST)
        
class SendResetPassView(generics.CreateAPIView):
    serializer_class = ResetPasswordRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_data = serializer.validate(request.data)
        
        reset_link = f'http://localhost:3000/reset-password/{user_data[0]}/{user_data[1]}'
        if user_data:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY') )
            message = Mail(
                    from_email=From('jobpilot@ukr.net', 'Jobpilot'),
                    to_emails=To(user_data[2]),
                    subject='Jobpilot reset password request',
                    plain_text_content=reset_link
                )

            response = sg.send(message)
            print(response)
                
            return Response({'status':'success', 'detail': 'Password reset link sent.', 'user_id': user_data[0], 'token': user_data[1]})
        else:
            return Response({'status': 'error', 'detail': 'Error creating password reset link: user not found.'})
        
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Проверяем валидность данных
        uidb64 = request.data['uid_64']
        token_key = request.data['token']
        # Получаем данные из запроса
        password = serializer.create(request.data)
        user_id = urlsafe_base64_decode(uidb64).decode('utf-8')
        try:
            # Получаем пользователя по идентификатору
            user = CustomUser.objects.get(id=user_id)
        except:
            return Response({'status': 'error', 'detail': 'User not found.'}, status=400)

        try:
            token_obj = Token.objects.get(key=token_key)
        except:
            return Response({'status': 'error', 'detail': 'Token not found.'}, status=400)
        
        if password:
            
            print(password)
            user.set_password(password)
            user.save()

                # Удаляем токен пользователя
            token_obj.delete()
        else:
            return Response({'status': 'error', 'detail': "Passwords do not match."})
            
        return Response({'status': 'success', 'detail': 'Password changed successfully!', 'note': 'You must relogin'})
    
class ChangePasswordView(generics.CreateAPIView):
    serializer_class = ChangePasswordSerializer
    
    def create(self, request):
        serializer = self.get_serializer()
        current_password = request.data['current_password']
        user = CustomUser.objects.get(id=request.data['user_id'])
        
        if user.check_password(current_password):
            change_password = serializer.change(user, request.data)

            if change_password:
                return Response({'status':'success', 'detail': "Password changed successfully!"})       
            else:
                return Response({'status': 'error', 'detail': "new_password1 & new_password2 didnt match."})
        else:
            return Response({'status':'error', 'detail': "Wrong current password."}) 
        

class SaveEmployerView(generics.CreateAPIView):
    serializer_class = SaveEmployerSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        employer = Employer.objects.create(user=user)
        employer_created = serializer.update(employer, request.data)
        
        if not employer_created:
            return Response({"status": 'error', 'detail': "Error creating employer."})
        
        return Response({'status': "success", "detail": "Employer created successfully!"})
    
class ChangeEmployerCompanyInfoView(generics.CreateAPIView):
    serializer_class = ChangeEmployerCompanyInfoSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        employer = Employer.objects.get(user=user)
        employer_changed = serializer.update(employer, request.data)
        
        if not employer_changed:
            return Response({'status': 'error', 'detail': 'Error changing employer data.'})
        
        return Response({'status': "success", 'detail': 'Employer company info changed successfully!'})
    
    
class ChangeEmployerFoundingInfoView(generics.CreateAPIView):
    serializer_class = ChangeEmployerFoundingInfoSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        employer = Employer.objects.get(user=user)
        employer_changed = serializer.change_founding(employer, request.data)
        
        if not employer_changed:
            return Response({"status": 'error', 'detail': 'Failed to change employer`s founding info.'})
        
        return Response({'status':"success", 'detail': "Employer founding info changed successfully!"})
    
class CreateEmployerSocialView(generics.CreateAPIView):
    serializer_class = CreateEmployerSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        employer = Employer.objects.get(user=user)
        employer_link = EmployerSocialLink.objects.create(employer=employer)
        link_created = serializer.create(employer_link, request.data)
        
        if not link_created:
            return Response({'status': 'error', 'detail': 'Error creating link model'})
        
        return Response({'status': 'success', 'detail': "Link added successfully!"})        


class ChangeEmployerContactView(generics.CreateAPIView):
    serializer_class = ChangeEmployerContactSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        user = CustomUser.objects.get(id=request.data['user_id'])
        employer = Employer.objects.get(user=user)
        employer_changed = serializer.change(employer, request.data)
        
        if not employer_changed:
            return Response({'status': 'error', 'detail': 'Error changing employer contacts'})
        
        return Response({'status': 'success', 'detail': "Employer contacts changed successfully!"})
    
        

class ChangeCandidatePersonalView(generics.CreateAPIView):
    serializer_class = ChangeCandidatePersonalSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = request.data['user_id']
        user = CustomUser.objects.get(id=user_id)
        candidate_obj = Candidate.objects.get(user=user)
        candidate = serializer.update(candidate_obj, request.data)
        
        if not candidate:
            return Response({'status':'error', 'detail': "Error updating candidate."})
        
        return Response({'status': "success", 'detail': "Candidate info changed successfully!"})
    
        
class CreateResumeView(generics.CreateAPIView):
    serializer_class = CreateResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        candidate = Candidate.objects.get(user=user)
        resume = ResumeFile.objects.create(candidate=candidate)
        resume_created = serializer.create(resume, request.data)
        
        if not resume_created:
            return Response({'status': 'error', 'detail': "Error creating resume"})
        
        return Response({'status':"success", 'detail': "Resume created successfully!", 'resume_id': resume.id})
    
    
class ChangeResumeView(generics.CreateAPIView):
    serializer_class = ChangeResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resume = ResumeFile.objects.get(id=request.data['resume_id'])
        resume_changed = serializer.change(resume, request.data)
        
        if not resume_changed:
            return Response({'status': 'error', 'detail': 'Error changing resume'})
        
        return Response({'status': 'success', 'detail': 'Resume file changed successfully!'})
    

class DeleteResumeView(generics.CreateAPIView):
    serializer_class = DeleteResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resume = ResumeFile.objects.get(id=request.data['resume_id'])
        resume_deleted = serializer.delete_resume(resume, request.data)
        
        if not resume_deleted:
            return Response({'status': "error", "detail": "Error deleting resume"})
        
        return Response({"status": "success", "detail": "Resume deleted successfully!"})
    
class ChangeCandidateProfileView(generics.CreateAPIView):
    serializer_class = ChangeCandidateProfileSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        candidate = Candidate.objects.get(user=user)
        change_personal = serializer.change_profile(candidate, request.data)
        
        if not change_personal:
            return Response({'status': 'error', 'detail': "Failed to change profile candidate data."})
        
        return Response({'status': 'success', 'detail': 'Candidate`s profile data changed successfully!'})
    
class CreateCandidateSocialView(generics.CreateAPIView):
    serializer_class = CreateCandidateSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = CustomUser.objects.get(id=request.data['user_id'])
        candidate = Candidate.objects.get(user=user)
        candidate_social = CandidateSocialLink.objects.create(candidate=candidate)
        set_link = serializer.create_link(candidate_social, request.data)
        
        if not set_link:
            return Response({'status': 'error', 'detail': "Error creating candidate social link"})
        
        return Response({'status': 'success', 'detail': 'Candidate social network link created successfully!', 'id': set_link.id})
    

class DeleteCandidateSocialView(generics.CreateAPIView):
    serializer_class = DeleteCandidateSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = CandidateSocialLink.objects.get(id=request.data['id'])
        delete_link = serializer.delete_link(link)
        
        if not delete_link:
            return Response({'status': 'error', 'detail': "Error deleting candidate social link"})
        
        return Response({'status': 'success', 'detail': "Deleted successfully!"})
    
    
    
    
    
            