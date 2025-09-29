# complaints/services.py
from django.conf import settings
from django.core.mail import send_mail

def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    if not to_email:
        return False
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
        return True
    except Exception:
        return False

def send_sms_notification(to_phone: str, body: str) -> bool:
    if not to_phone:
        return False
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_num = settings.TWILIO_FROM_NUMBER
    if not (sid and token and from_num):
        return False
    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(to=to_phone, from_=from_num, body=body)
        return True
    except Exception:
        return False
