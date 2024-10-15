import smtplib
from collections.abc import Iterable
from functools import cached_property
from logging import getLogger
from ssl import PROTOCOL_TLS_CLIENT, SSLContext, SSLError, create_default_context
from threading import RLock
from typing import Optional, Union

from src.core.config import settings
from src.services.mail.email.backend.base import EmailBackendABC
from src.services.mail.email.backend.exceptions import EmailBackendError
from src.services.mail.email.message import EmailMessage

logger = getLogger(__name__)


class EmailSMTPBackend(EmailBackendABC):
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[int] = None,
        use_tls: Optional[bool] = None,
        use_ssl: Optional[bool] = None,
        ssl_keyfile=None,
        ssl_certfile=None,
        fail_silently: bool = False,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently)

        self.host = host or settings.EMAIL.HOST
        self.port = port or settings.EMAIL.PORT
        self.username = settings.EMAIL.USERNAME if username is None else username
        self.password = settings.EMAIL.PASSWORD if password is None else password
        self.use_tls = settings.EMAIL.USE_TLS if use_tls is None else use_tls
        self.use_ssl = settings.EMAIL.USE_SSL if use_ssl is None else use_ssl
        self.timeout = settings.EMAIL.TIMEOUT if timeout is None else timeout

        if self.use_ssl and self.use_tls:
            raise ValueError("Нельзя передавать сразу и use_ssl и use_tls")

        self.ssl_keyfile = (
            settings.EMAIL.SSL_KEYFILE if ssl_keyfile is None else ssl_keyfile
        )
        self.ssl_certfile = (
            settings.EMAIL.SSL_CERTFILE if ssl_certfile is None else ssl_certfile
        )

        self.connection: Optional[smtplib.SMTP] = None
        self._lock = RLock()

    def send_messages(
        self, messages: Union[list[EmailMessage], Iterable[EmailMessage]]
    ) -> int:
        if not messages:
            return 0
        with self._lock:
            new_conn = self._open()
            if not self.connection or new_conn is None:
                return 0

            num_sent = 0
            try:
                for message in messages:
                    sent = self._send(message)
                    if sent:
                        num_sent += 1
            except smtplib.SMTPException as e:
                if not self.fail_silently:
                    logger.warning("Ошибка при отправке сообщения", exc_info=e)
                    raise EmailBackendError(reason=str(e))
            finally:
                self._close()

        return num_sent

    def _send(self, message: EmailMessage) -> bool:
        if not message.recipients:
            return False

        msg = message.mime_message()
        self.connection.sendmail(
            message.from_email, message.recipients, msg.as_bytes(linesep="\r\n")
        )
        return True

    def _open(self) -> Optional[bool]:
        if self.connection:
            return False

        connection_params = {}
        if self.timeout:
            connection_params["timeout"] = self.timeout
        if self.use_ssl:
            connection_params["context"] = self.ssl_context

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                **connection_params,
            )

            if not self.use_ssl and self.use_tls:
                self.connection.starttls()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
        except ConnectionError:
            if not self.fail_silently:
                raise EmailBackendError("Ошибка внешнего сервиса отправки")
        except (smtplib.SMTPException, SSLError) as e:
            if not self.fail_silently:
                raise EmailBackendError(reason=str(e))

        return True

    def _close(self) -> None:
        if self.connection is None:
            return

        try:
            self.connection.quit()
        except (SSLError, smtplib.SMTPServerDisconnected):
            self.connection.close()
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise EmailBackendError

        finally:
            self.connection = None

    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            ssl_context = SSLContext(protocol=PROTOCOL_TLS_CLIENT)
            ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return ssl_context

        return create_default_context()

    @property
    def connection_class(self):
        return smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
