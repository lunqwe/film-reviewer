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
from .serializers import UserSerializer, LoginSerializer, SendVerificationSerializer, CheckVerificationSerializer, ResetPasswordRequestSerializer, ResetPasswordSerializer
from .models import CustomUser, Verificator, Candidate, Employer



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
        user = CustomUser.objects.get(id=request.data['user_id'])
        user_data = serializer.validate(request.data)
        
        reset_link = f'http://localhost:3000/reset-password/{user_data[0]}/{user_data[1]}'
        if user:
            if user_data:
                sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY') )
                message = Mail(
                        from_email=From('jobpilot@ukr.net', 'Jobpilot'),
                        to_emails=To(user.email),
                        subject='Jobpilot reset password request',
                        plain_text_content=reset_link
                    )

                response = sg.send(message)
                print(response)
                
                return Response({'status':'success', 'detail': 'Password reset link sent.', 'user_id': user_data[0], 'token': user_data[1]})
            else:
                return Response({'status': 'error', 'detail': 'Error creating password reset link: user not found.'})
        else:
            return Response({'status': 'error', 'detail': "User not found."})
        
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Проверяем валидность данных

        # Получаем данные из запроса
        password = serializer.create(request.data)
        user_id = urlsafe_base64_decode(uidb64).decode('utf-8')
        try:
            # Получаем пользователя по идентификатору
            user = CustomUser.objects.get(id=user_id)
        except:
            return Response({'status': 'error', 'detail': 'User not found.'}, status=400)

        try:
                # Получаем токен пользователя
            token_obj = Token.objects.get(user=user)
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
        
    