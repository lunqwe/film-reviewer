from django.contrib import admin
from .models import CustomUser, Verificator, Employer, Candidate, CandidateSocialLink, EmployerSocialLink
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Verificator)
admin.site.register(Employer)
admin.site.register(EmployerSocialLink)
admin.site.register(Candidate)
admin.site.register(CandidateSocialLink)
