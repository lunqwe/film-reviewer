from rest_framework.response import Response
from rest_framework import status

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