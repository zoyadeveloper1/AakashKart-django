from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_reset_email(user, reset_url):
    message = render_to_string('accounts/reset_password_email.html', {
        'user': user,
        'reset_url': reset_url,
    })

    mail = EmailMessage(
        subject="Reset Your Password",
        body=message,
        to=[user.email],
    )
    mail.content_subtype = "html"
    mail.send()
