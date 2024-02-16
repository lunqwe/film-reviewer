import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os
from rest_framework.response import Response
from rest_framework import status
from common.services import *