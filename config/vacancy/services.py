import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os
from rest_framework.response import Response
from rest_framework import status
from common.services import *
from user.models import Employer
from .models import Vacancy


def create_vacancy(data):
    user = get_user(data['user_id'])
    employer = get_object(Employer, user=user)
    data['author'] = employer
    del data['user_id']
    create_object(Vacancy, data)
    return get_response('success', 'Vacancy created successfully!', status=status.HTTP_201_CREATED)