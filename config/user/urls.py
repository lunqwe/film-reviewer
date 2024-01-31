from django.urls import path, include
from .views import CreateUserView, LoginView, VerifyEmailView, CheckVerificationView, SendResetPassView, ResetPasswordView, SaveEmployerView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification/', VerifyEmailView.as_view(), name='send-verification'),
    path('check-verification/', CheckVerificationView.as_view(), name='check-verification'),
    path('password-reset-request/', SendResetPassView.as_view(), name='password-reset-request'),
    path('reset-password/', ResetPasswordView.as_view(), name='password-reset'),
    path('create-employer/', SaveEmployerView.as_view(), name='create-employer')
]