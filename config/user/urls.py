from django.urls import path, include
from .views import CreateUserView, LoginView, VerifyEmailView, CheckVerificationView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification/', VerifyEmailView.as_view(), name='send-verification'),
    path('check-verification/', CheckVerificationView.as_view(), name='check-verification')
]