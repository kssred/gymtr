from .email.backend import (
    EmailBackendABC,
    EmailConsoleBackend,
    EmailLocmemBackend,
    EmailSMTPBackend,
)
from .email.backend.exceptions import EmailBackendError
from .email.message import EmailMessage, EmailMultiAlternatives
from .email.service import (
    EmailService,
    email_service,
    get_email_service,
)

email_outbox: list[EmailMessage] = []

__all__ = [
    "EmailBackendABC",
    "EmailConsoleBackend",
    "EmailLocmemBackend",
    "EmailSMTPBackend",
    "EmailBackendError",
    "EmailMultiAlternatives",
    "EmailMessage",
    "EmailService",
    "email_service",
    "get_email_service",
]
