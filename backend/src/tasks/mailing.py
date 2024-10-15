from celery import shared_task

from src.services.mail import email_service


@shared_task
def send_mail(
    subject: str, body: str, recipients: list[str], fail_silently: bool = False
):
    email_service.send_email(
        subject=subject, body=body, recipients=recipients, fail_silently=fail_silently
    )
