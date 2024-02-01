from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateUserView, LoginView, VerifyEmailView, CheckVerificationView, SendResetPassView, ResetPasswordView, SaveEmployerView,  ChangeCandidatePersonalView, CreateResumeView, ChangeResumeView, DeleteResumeView, ChangeEmployerCompanyInfoView


urlpatterns = [
    path('register/', CreateUserView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification/', VerifyEmailView.as_view(), name='send-verification'),
    path('check-verification/', CheckVerificationView.as_view(), name='check-verification'),
    path('password-reset-request/', SendResetPassView.as_view(), name='password-reset-request'),
    path('reset-password/', ResetPasswordView.as_view(), name='password-reset'),
    path('create-employer/', SaveEmployerView.as_view(), name='create-employer'),
    path('change-employer-company-info/', ChangeEmployerCompanyInfoView.as_view(), name='change-company-info'),
    path('change-candidate-personal/', ChangeCandidatePersonalView.as_view(), name='change-candidate-personal'),
    path('create-resume/', CreateResumeView.as_view(), name='create-resume'), 
    path('change-resume/', ChangeResumeView.as_view(), name='change-resume'),
    path('delete-resume/', DeleteResumeView.as_view(), name='delete-resume'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
