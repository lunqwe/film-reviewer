from django.contrib import admin
from .models import CustomUser, Verificator, Employer, Candidate

admin.site.register(CustomUser)
admin.site.register(Verificator)
admin.site.register(Employer)
admin.site.register(Candidate)

