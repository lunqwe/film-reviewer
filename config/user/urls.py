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
    path('manage-employer-links/', EmployerSocialLinksView.as_view(), name='add-employer-link'),
    path('change-employer-contacts/', ChangeEmployerContactView.as_view(), name='change-employer-contact'),
    path('change-candidate-personal/', ChangeCandidatePersonalView.as_view(), name='change-candidate-personal'),
    path('change-candidate-profile/', ChangeCandidateProfileView.as_view(), name='change-candidate-profile'),
    path('manage-candidate-links/', CandidateSocialLinksView.as_view(), name='add-candidate-link'),
    path('change-candidate-account-settings/', ChangeCandidateAccountSettingsView.as_view(), name='change-candidate-account-settings'),
    path('change-candidate-notifications-and-alerts/', ChangeCandidateNotificationsAndAlertsView.as_view(), name='change-notifications-and-alerts'),
    path('change-candidate-privacy/', ChangeCandidatePrivacyView.as_view(), name='change-privacy'),
    path('create-resume/', CreateResumeView.as_view(), name='create-resume'), 
    path('change-resume/', ChangeResumeView.as_view(), name='change-resume'),
    path('delete-resume/', DeleteResumeView.as_view(), name='delete-resume'),
    path('get-user/<token>', GetUserView.as_view(), name='get_user'),
    path('delete-user/', DeleteUserView.as_view(), name='delete-user'),
    # path('test-image/', TestImageView.as_view(), name='test'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#737dd57799662da898c5100ec409ece207b18dbb