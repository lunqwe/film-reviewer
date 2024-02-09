from .models import CustomUser, Employer, Candidate, EmployerSocialLink, CandidateSocialLink
import sendgrid
from sendgrid.helpers.mail import Mail, From, To
import os




def get_user(**kwargs):
    try:
        user = CustomUser.objects.get(**kwargs)
        return user
    except:
        return False
    
    
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
        print(response)
    except Exception as e:
        print("Error while sending email")
        print(e)