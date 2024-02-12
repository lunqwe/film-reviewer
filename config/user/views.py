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
from .models import CustomUser, Verificator, Candidate, Employer, ResumeFile, EmployerSocialLink
from .services import get_object, send_email, create_object, get_response, error_detail



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

            user = create_object(CustomUser, **serializer.validated_data)
            print(user)
            user.set_password(password)
            user.save()
            
            if user_type:
                if user_type == 'candidate':
                    candidate = create_object(Candidate, user=user)
                
                elif user_type == 'employer':
                    employer = create_object(Employer, user=user)
                    
                else:
                    return get_response('error', "Wrong user status.", status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                return get_response('error', 'User status specification required.', status=status.HTTP_400_BAD_REQUEST)

            return get_response('success', "User created successfully!", {'id': user.id}, status=status.HTTP_201_CREATED)
        
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
                    generated_code = random.randint(100000,1000000)
                    try:
                        verificator = Verificator.objects.filter(user=user).only("code", 'time_created')
                        if len(verificator) == 1:
                            verificator = verificator[0]
                            print('get')
                        elif len(verificator) > 1:
                            raise ValueError('User has more than 1 verificator. Code error')
                        
                        elif len(verificator) < 1:
                            verificator = create_object(Verificator, user=user)
                            print('create')
                    except Exception as e:
                        print(e)
                    print(verificator)
                    print(generated_code)
                    verificator.code = str(generated_code)
                    verificator.time_created = timezone.now()
                    verificator.save()
                    
                    mail = send_email(user_email=user.email, subject='Jobpilot email verification', email_content=str(generated_code))
                    if mail:
                        return get_response('success', 'Verification message sent!', status=status.HTTP_201_CREATED)
                    else:
                        return get_response('error', 'Failed to send email. (401 Unauthorized) ', status=status.HTTP_408_REQUEST_TIMEOUT)
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
            check_verification = serializer.verificate(request.data)
            
            if check_verification == 'already_verified':
                return get_response('error', 'User email is already verified.', status=status.HTTP_400_BAD_REQUEST)

            if check_verification == 'expired':
                return get_response('error', 'Verification code expired.', status=status.HTTP_408_REQUEST_TIMEOUT)
            
            elif check_verification == 'wrong_code':
                return get_response('error', "Wrong code", status=status.HTTP_401_UNAUTHORIZED)
            
            elif check_verification == 'success':
                user = get_object(CustomUser, id=request.data['user_id'], only_values=('verified_email'))
                user.verified_email = True
                user.save()
                return get_response('success', 'Verificated successfully!', status=status.HTTP_201_CREATED)
            
            else:
                return get_response('error', 'Verificator never existed.', status=status.HTTP_400_BAD_REQUEST)
            
        except serializers.ValidationError as e:
            return error_detail(e)
        
            
class SendResetPassView(generics.CreateAPIView):
    serializer_class = ResetPasswordRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            user_data = serializer.validate(request.data)
            serializer.is_valid(raise_exception=True)
            
            reset_link = f'http://localhost:3000/reset-password/{user_data[0]}/{user_data[1]}'
            if user_data:
                mail = send_email(user_email=user_data[2], subject='Jobpilot reset password request', email_content=reset_link)
                if mail:
                    
                    return get_response('success', 'Password reset link sent.', {'user_id': user_data[0], 'token': user_data[1]}, status=status.HTTP_201_OK)
                else:
                    
                    return get_response('error', "Error sending email.")
            else:
                return get_response('error', 'Error creating password reset link: user not found.')
            
        except serializers.ValidationError as e:
            return error_detail(e)
        
        
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            uidb64 = request.data['uid_64']
            token_key = request.data['token']

            password = serializer.validate(request.data)
            user_id = urlsafe_base64_decode(uidb64).decode('utf-8')
            try:
                user = get_object(CustomUser, id=user_id)
            except:
                return get_response('error', 'User not found.', status=status.HTTP_401_UNAUTHORIZED)
            try:
                token_obj = get_object(Token, key=token_key)
            except:
                return get_response('error', 'Token not found.', status=status.HTTP_404_NOT_FOUND)
            
            if password:
                user.set_password(password)
                user.save()
                token_obj.delete()
            else:
                return get_response('error', "Passwords do not match.")
                
            return get_response('success', 'Password changed successfully!', {'note': 'You must relogin'})
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangePasswordView(generics.CreateAPIView):
    serializer_class = ChangePasswordSerializer
    
    def create(self, request):
        serializer = self.get_serializer()
        try:
            serializer.is_valid(raise_exception=True)
            current_password = request.data['current_password']
            user = get_object(CustomUser, id=request.data['user_id']).defer()
            
            if user.check_password(current_password):
                change_password = serializer.change(user, request.data)

                if change_password:
                    return get_response('success', "Password changed successfully!")       
                else:
                    return get_response('error', "new_password1 & new_password2 didnt match.")
            else:
                return get_response('error', "Wrong current password.") 
            
        except serializers.ValidationError as e:
            return error_detail(e)
        

class SaveEmployerView(generics.CreateAPIView):
    serializer_class = SaveEmployerSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = CustomUser.objects.get(id=request.data['user_id'])
            employer = Employer.objects.create(user=user)
            employer_created = serializer.update(employer, request.data)
            
            if not employer_created:
                return get_response('error', "Error creating employer.")
            
            return get_response("success", "Employer created successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangeEmployerCompanyInfoView(generics.CreateAPIView):
    serializer_class = ChangeEmployerCompanyInfoSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = get_object(CustomUser, id=request.data['user_id'], defer=())
            employer = get_object(Employer, user=user)
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
            
            user = get_object(CustomUser, id=request.data['user_id'])
            employer = get_object(Employer, user=user)
            employer_changed = serializer.change_founding(employer, request.data)
            
            if not employer_changed:
                return get_response('error', 'Failed to change employer`s founding info.')
            
            return get_response("success", "Employer founding info changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class CreateEmployerSocialView(generics.CreateAPIView):
    serializer_class = CreateEmployerSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_object(CustomUser, id=request.data['user_id'])
            employer = get_object(Employer, user=user)
            employer_link = create_object(EmployerSocialLink, employer=employer)
            link_created = serializer.create(employer_link, request.data)
            
            if not link_created:
                return get_response('error', 'Error creating link model')
            
            return get_response('success', "Link added successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)


class ChangeEmployerContactView(generics.CreateAPIView):
    serializer_class = ChangeEmployerContactSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_object(CustomUser, id=request.data['user_id'])
            employer = get_object(Employer, user=user)
            employer_changed = serializer.change(employer, request.data)
            
            if not employer_changed:
                return get_response('error', 'Error changing employer contacts')
            
            return get_response('success', "Employer contacts changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
        

class ChangeCandidatePersonalView(generics.CreateAPIView):
    serializer_class = ChangeCandidatePersonalSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate_obj = get_object(Candidate, user=user)
            candidate = serializer.update(candidate_obj, request.data)
            
            if not candidate:
                return get_response('error', "Error updating candidate.")
            
            return get_response("success", "Candidate info changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
        
class CreateResumeView(generics.CreateAPIView):
    serializer_class = CreateResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            resume = create_object(ResumeFile, {'candidate': candidate})
            
            if not resume:
                return get_response('error', "Error creating resume")
            
            return get_response("success", "Resume created successfully!", {'resume_id': resume.id})
        
        except serializers.ValidationError as e:
            return error_detail(e)
        
    
class ChangeResumeView(generics.CreateAPIView):
    serializer_class = ChangeResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            resume =get_object(ResumeFile, id=request.data['resume_id'])
            resume_changed = serializer.change(resume, request.data)
            
            if not resume_changed:
                return get_response('error', 'Error changing resume')
            
            return get_response('success', 'Resume file changed successfully!')
        
        except serializers.ValidationError as e:
            return error_detail(e)
    

class DeleteResumeView(generics.CreateAPIView):
    serializer_class = DeleteResumeSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            resume = get_object(ResumeFile, id=request.data['resume_id'])
            resume_deleted = serializer.delete_resume(resume, request.data)
            if not resume_deleted:
                return get_response("error", "Error deleting resume")
            
            return get_response("success", "Resume deleted successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class ChangeCandidateProfileView(generics.CreateAPIView):
    serializer_class = ChangeCandidateProfileSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            change_personal = serializer.change_profile(candidate, request.data)
            
            if not change_personal:
                return get_response('error', "Failed to change profile candidate data.")
            
            return get_response('success', 'Candidate`s profile data changed successfully!')
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class CreateCandidateSocialView(generics.CreateAPIView):
    serializer_class = CreateCandidateSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            print(candidate)
            candidate_social = create_object(CandidateSocialLink, {'candidate': candidate,
                                                                   "social_network": request.data['social_network'],
                                                                   'link': request.data['link']})
            
            if not candidate_social:
                return get_response('error', "Error creating candidate social link")
            
            return get_response('success', 'Candidate social network link created successfully!', {'id': candidate_social.id})
        
        except serializers.ValidationError as e:
            return error_detail(e)
    

class DeleteCandidateSocialView(generics.CreateAPIView):
    serializer_class = DeleteCandidateSocialSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            link = get_object(CandidateSocialLink, id=request.data['id'])
            delete_link = serializer.delete_link(link)
            
            if not delete_link:
                return get_response('error', "Error deleting candidate social link")
            
            return get_response('success', "Deleted successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class ChangeCandidateAccountSettingsView(generics.CreateAPIView):
    serializer_class = ChangeCandidateAccountSettingsSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate settings')
            
            return get_response('success', "Candidate settings changed successfully!")
        
        except serializers.ValidationError as e:
            return error_detail(e)
    
class ChangeCandidateNotificationsView(generics.CreateAPIView):
    serializer_class = ChangeCandidateNotificationsSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate notifications')
            
            return get_response('success', "Candidate notifications changed successfully!")
        except serializers.ValidationError as e:
            return error_detail(e)
            
class ChangeCandidatePrivacyView(generics.CreateAPIView):
    serializer_class = ChangeCandidatePrivacySerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_object(CustomUser, id=request.data['user_id'])
            candidate = get_object(Candidate, user=user)
            change_settings = serializer.change_settings(candidate, request.data)
            
            if not change_settings:
                return get_response('error', 'Failed to change candidate privacy')
            
            return get_response('success', "Candidate privacy changed successfully!")
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

            user_data = {
                'full_name': user.full_name,
                'email': user.email,
                'status': user.status,
                'verified_email': user.verified_email
            }

            if user.status == 'employer':
                employer = get_object(Employer, user=user)
                employer_data = {
                    'user_id': user.id,
                    'logo': employer.logo.url,
                    "banner": employer.banner.url,
                    "company_name": employer.company_name,
                    "about": employer.about,
                    "organization_type": employer.organization_type,
                    "industry_types": employer.industry_types,
                    "team_size": employer.team_size,
                    "website": employer.website,
                    "year_of_establishment": employer.year_of_establishment,
                    "company_vision": employer.company_vision,
                    "map_location": employer.map_location,
                    "phone_number": employer.phone_number,
                    "email": employer.email
                }
                return get_response('success', additional={'user': {"user_data": user_data, "employer_data": employer_data}}, status=status.HTTP_200_OK)
            
            
            elif user.status == 'candidate':
                candidate = get_object(Candidate, user=user)
                candidate_data = {
                    "full_name": candidate.full_name,
                    "headline": candidate.headline,
                    "experiences": candidate.experiences,
                    "educations": candidate.educations,
                    "website": candidate.website,
                    "nationality": candidate.nationality,
                    "date_of_birth": candidate.date_of_birth,
                    "gender": candidate.gender,
                    'marital_status': candidate.marital_status,
                    "biography": candidate.biography,
                    "map_location": candidate.map_location,
                    "phone_number": candidate.phone_number,
                    "shortlist": candidate.shortlist,
                    "expire": candidate.expire,
                    "five_job_alerts": candidate.five_job_alerts,
                    "profile_saved": candidate.profile_saved,
                    "rejection": candidate.rejection,
                    "profile_privacy": candidate.profile_privacy,
                    "resume_privacy": candidate.resume_privacy,
                }
                return get_response('success', additional={'user': {"user_data": user_data, "candidate_data": candidate_data}}, status=status.HTTP_200_OK)
            
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
                return get_response('error', "Error deleting user")
            
            return Response('success', "User deleted successfully!")
        
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
        