import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os
from rest_framework.response import Response
from rest_framework import status
from user.models import CustomUser


def create_object(model_class, data_dict):
    try:
        model_instance = model_class.objects.create(**data_dict)
        return model_instance
    
    except Exception as e:
        print(f"Error creating object: {e}")
        return None


def get_object(model, **kwargs):
    try:
        model = model.objects.get(**kwargs)
        return model
    except Exception as e:
        print(e)
        raise ValueError(e)
    
def get_user(id):
    return get_object(CustomUser, id=id)

def get_obj_by_user_id(model, user_id):
    user = get_object(CustomUser, id=user_id)
    return get_object(model, user=user)
    
    
def send_email(user_email, subject, email_content):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY') )
        message = Mail(
                    from_email=From('jobpilot@ukr.net', 'Jobpilot'),
                    to_emails=user_email,
                    subject=subject,
                    plain_text_content=email_content
                )

        response = sg.send(message)
        return response
    except Exception as e:
        print("Error while sending email")
        print(e)
        return False
    

def get_response(response_status, detail=(), additional: dict=(),  status=()):
    response_dict = {}
    if response_status:
        response_dict['status'] = response_status
    if detail:
        response_dict['detail'] = detail
    if additional:
        for key, value in additional.items():
            response_dict[key] = value  
            
    
            
    return Response(response_dict, status)


def error_detail(e):
    errors = e.detail
    
    error_messages = []
    for field, messages in errors.items():
        error_messages.append(f'{field}: {messages[0].__str__()}')
    
    return get_response('error', additional={'detail': error_messages[0]}, status=status.HTTP_400_BAD_REQUEST)

def change_data(instance, fields_to_update, validated_data):
    print(validated_data)
    for field in fields_to_update:
        if validated_data.get(field):
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
            print(instance.field)
    instance.save()
    return instance