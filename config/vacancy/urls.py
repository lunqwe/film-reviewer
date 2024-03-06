from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('create/', CreateVacancyView.as_view(), name='create-vacancy'),
    path('get-vacancies/', GetVacanciesView.as_view(), name='get-vacancies')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)