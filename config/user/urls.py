from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('register/', CreateUserView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification/', VerifyEmailView.as_view(), name='send-verification'),
    path('check-verification/', CheckVerificationView.as_view(), name='check-verification'),
    path('password-reset-request/', SendResetPassView.as_view(), name='password-reset-request'),
    path('reset-password/', ResetPasswordView.as_view(), name='password-reset'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('create-employer/', SaveEmployerView.as_view(), name='create-employer'),
    path('change-company-info/', ChangeEmployerCompanyInfoView.as_view(), name='change-company-info'),
    path('change-founding-info/', ChangeEmployerFoundingInfoView.as_view(), name='change-founding-info'),
    path('add-employer-link/', CreateEmployerSocialView.as_view(), name='add-employer-link'),
    path('change-employer-contacts/', ChangeEmployerContactView.as_view(), name='change-employer-contact'),
    path('change-candidate-personal/', ChangeCandidatePersonalView.as_view(), name='change-candidate-personal'),
    path('change-candidate-profile/', ChangeCandidateProfileView.as_view(), name='change-candidate-profile'),
    path('add-candidate-link/', CreateCandidateSocialView.as_view(), name='add-candidate-link'),
    path('delete-candidate-link/', DeleteCandidateSocialView.as_view(), name='delete-candidate-link'),
    path('change-candidate-account-settings', ChangeCandidateAccountSettingsView.as_view(), name='change-candidate-account-settings'),
    path('create-resume/', CreateResumeView.as_view(), name='create-resume'), 
    path('change-resume/', ChangeResumeView.as_view(), name='change-resume'),
    path('delete-resume/', DeleteResumeView.as_view(), name='delete-resume'),
    path('get-user/', GetUserView.as_view(), name='get_user'),
    path('delete-user/', DeleteUserView.as_view(), name='delete-user')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
