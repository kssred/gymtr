from typing import Optional

from src.core.config import settings
from src.services.mail.email.backend import EmailBackendABC
from src.services.mail.email.backend.exceptions import EmailBackendError
from src.services.mail.email.message import EmailMultiAlternatives
from src.services.mail.exceptions import MailServiceError
from src.utils.loading import import_string


class EmailService:
    """
    Сервис по логике работы с emails сообщениями

    :param email_backend: Способ, которым будет отправлено сообщение
    """

    def __init__(self, email_backend: EmailBackendABC):
        self.backend = email_backend

    def send_email(
        self,
        subject: str,
        body: str,
        recipients: list[str],
        from_email: Optional[str] = None,
        bcc: Optional[list[str]] = None,
        cc: Optional[list[str]] = None,
        attachments: Optional[list] = None,
        reply_to: Optional[list[str]] = None,
        alternatives: Optional[list] = None,
        fail_silently: bool = False,
    ) -> int:
        """
        Отправить Email сообщение

        :raises EmailServiceError: Ошибка отправки сообщения
        :return: Количество успешно отправленных сообщений
        """
        self.backend.fail_silently = fail_silently

        message = EmailMultiAlternatives(
            recipients,
            subject,
            body,
            from_email,
            bcc,
            cc,
            attachments,
            reply_to=reply_to,
            alternatives=alternatives,
        )

        try:
            with self.backend as email_backend:
                sent_count = email_backend.send_messages([message])
        except EmailBackendError as e:
            raise MailServiceError(reason=e.reason) from e

        return sent_count


backend_class = import_string(settings.EMAIL.BACKEND)
backend = backend_class(
    host=settings.EMAIL.HOST,
    port=settings.EMAIL.PORT,
    username=settings.EMAIL.USERNAME,
    password=settings.EMAIL.PASSWORD,
)

email_service = EmailService(email_backend=backend)


async def get_email_service() -> EmailService:
    yield EmailService(email_backend=backend)
