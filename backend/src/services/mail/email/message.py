from email import generator, encoders, charset as charset_module
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from io import StringIO, BytesIO
from mimetypes import guess_type
from os import PathLike
from pathlib import Path
from typing import Iterable, Optional, Any, Union

from src.core.config import settings

# Название возможных заголовков (RFC 5322)
ADDRESS_HEADERS = {
    "from",
    "sender",
    "reply-to",
    "to",
    "cc",
    "bcc",
    "resent-from",
    "resent-sender",
    "resent-to",
    "resent-cc",
    "resent-bcc",
}
RFC5322_EMAIL_LINE_LENGTH_LIMIT = 998

# Отказываемся от base64 кодирования тела сообщения, чтобы избежать некоторые спам фильтры
utf8_charset = charset_module.Charset("utf-8")
utf8_charset.body_encoding = None  # type: ignore
utf8_charset_qp = charset_module.Charset("utf-8")
utf8_charset_qp.body_encoding = charset_module.QP

DEFAULT_MIME_TYPE = "application/octet-stream"

RecipientsType = Union[list[str], tuple[str, ...]]


class MIMEMixin:
    def as_string(self, unixfrom=False, linesep="\n") -> str:
        """Обёртка над обычным as_string(), чтобы не искажать строки, начинающиеся с 'From'"""
        fp = StringIO()
        g = generator.Generator(fp, mangle_from_=False)
        g.flatten(self, unixfrom=unixfrom, linesep=linesep)  # type: ignore
        return fp.getvalue()

    def as_bytes(self, unixfrom=False, linesep="\n") -> bytes:
        """Обёртка над обычным as_bytes(), чтобы не искажать строки, начинающиеся с 'From'"""
        fp = BytesIO()
        g = generator.BytesGenerator(fp, mangle_from_=False)
        g.flatten(self, unixfrom=unixfrom, linesep=linesep)  # type: ignore
        return fp.getvalue()


class SafeMIMEText(MIMEMixin, MIMEText):
    def __init__(self, _text, _subtype: str = "plain", _charset: Optional[str] = None):
        self.encoding = _charset
        MIMEText.__init__(self, _text, _subtype=_subtype, _charset=_charset)

    def set_payload(self, payload, charset=None):
        if charset == "utf-8" and not isinstance(charset, charset_module.Charset):
            has_long_lines = any(
                len(line.encode(errors="surrogateescape"))
                > RFC5322_EMAIL_LINE_LENGTH_LIMIT
                for line in payload.splitlines()
            )
            charset = utf8_charset_qp if has_long_lines else utf8_charset
        MIMEText.set_payload(self, payload, charset=charset)


class SafeMIMEMultipart(MIMEMixin, MIMEMultipart):
    def __init__(
        self, _subtype="mixed", boundary=None, _subparts=None, encoding=None, **_params
    ):
        self.encoding = encoding
        MIMEMultipart.__init__(self, _subtype, boundary, _subparts, **_params)


class EmailMessage:
    content_subtype = "plain"
    encoding = "utf-8"

    def __init__(
        self,
        to: RecipientsType,
        subject: str = "",
        body: str = "",
        from_email: Optional[str] = None,
        bcc: Optional[RecipientsType] = None,
        cc: Optional[RecipientsType] = None,
        attachments: Optional[list[tuple[str | MIMEBase, Any, str] | None]] = None,
        headers: Optional[dict] = None,
        reply_to: Optional[RecipientsType] = None,
    ):
        self.to = to
        self.subject = subject
        self.body = body
        self.from_email = from_email or settings.EMAIL.FROM_EMAIL
        self.bcc = bcc or []
        self.cc = cc or []
        self.attachments: list[tuple[str | MIMEBase, Any, str] | None] = []
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, MIMEBase):
                    self.attach(attachment)
                else:
                    self.attach(*attachment)

        self.reply_to = reply_to or []
        self.extra_headers = headers or {}

    def mime_message(self) -> MIMEMultipart | SafeMIMEText:
        """Получить сообщение в его MIME представлении"""

        msg = SafeMIMEText(self.body, self.content_subtype, self.encoding)
        msg = self._create_message(msg)

        msg["Subject"] = self.subject
        msg["From"] = self.extra_headers.get("From", self.from_email)
        self._set_list_header(msg, "To", self.to)
        self._set_list_header(msg, "Cc", self.cc)
        self._set_list_header(msg, "Reply-To", self.reply_to)

        header_names = [key.lower() for key in self.extra_headers]
        if "date" not in header_names:
            msg["Date"] = formatdate()
        if "message-id" not in header_names:
            msg["Message-ID"] = make_msgid()
        for name, value in self.extra_headers.items():
            if name.lower() != "from":
                msg[name] = value

        return msg

    def attach(
        self,
        filename: Union[str, MIMEBase, None] = None,
        content: Union[str, bytes, None] = None,
        mimetype: Optional[str] = None,
    ) -> None:
        """Прикрепить файл к сообщению"""
        if isinstance(filename, MIMEBase):
            if content or mimetype:
                raise ValueError(
                    "Значения для content и mimetype не должны передаваться, когда в filename передан MIMEBase"
                )
        elif not content:
            raise ValueError("Значение для content должно быть передано")

        attachment_mimetype = mimetype or guess_type(filename)[0] or DEFAULT_MIME_TYPE
        basetype, subtype = attachment_mimetype.split("/", 1)

        if basetype == "text":
            if isinstance(content, bytes):
                try:
                    content = content.decode()
                except UnicodeDecodeError:
                    attachment_mimetype = DEFAULT_MIME_TYPE

        self.attachments.append((filename, content, attachment_mimetype))

    def attach_file(self, path: PathLike, mimetype: Optional[str] = None) -> None:
        """Прикрепить файл из файловой системы ОС к сообщению"""
        file_path = Path(path)
        content = file_path.read_bytes()

        self.attach(file_path.name, content, mimetype)

    def _create_message(
        self, message: SafeMIMEText
    ) -> SafeMIMEMultipart | SafeMIMEText:
        return self._create_attachments(message)

    def _create_attachments(
        self, message: SafeMIMEText | SafeMIMEMultipart
    ) -> SafeMIMEText | SafeMIMEMultipart:
        """Создаёт и добавляет к message все добавленные вложения"""
        if self.attachments:
            body_msg = message
            message = SafeMIMEMultipart(_subtype="mixed", encoding=self.encoding)

            if self.body or body_msg.is_multipart():
                message.attach(body_msg)
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    message.attach(attachment)
                # TODO подумать надо ли такое
                else:
                    message.attach(self._create_attachment(*attachment))

        return message

    def _create_attachment(
        self, filename: str, content, mimetype: Optional[str] = None
    ) -> MIMEBase:
        """Создаёт вложение, которое можно отправлять по emails"""
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            file_header = ("utf-8", "", filename)
            attachment.add_header(
                "Content-Disposition", "attachment", filename=file_header
            )

        return attachment

    def _create_mime_attachment(self, content, mimetype: str) -> MIMEBase:
        """Создаёт вложение в MIME классе"""
        basetype, subtype = mimetype.split("/", 1)

        if basetype == "text":
            attachment = SafeMIMEText(content, subtype, self.encoding)
        else:
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            encoders.encode_base64(attachment)

        return attachment

    def _set_list_header(
        self,
        message: MIMEBase,
        header_name: str,
        values: Optional[Iterable[str | int]] = None,
    ) -> None:
        """
        Добавляет заголовок к сообщению

        :param message: Сообщение
        :param header_name: Название заголовка
        :param values: Список значений. Установит их, если значений нет в self.extra_headers
        """
        if values:
            try:
                value = self.extra_headers[header_name]
            except KeyError:
                value = ", ".join(str(v) for v in values)
            message[header_name] = value

    @property
    def recipients(self) -> list[str]:
        """Список получателей"""
        return [email for email in (self.to + self.bcc + self.cc) if email]


class EmailMultiAlternatives(EmailMessage):
    """Класс сообщения с разными альтернативными представлениями"""

    alternative_subtype = "alternative"

    def __init__(
        self,
        to: list[str],
        subject: str = "",
        body: str = "",
        from_email: Optional[str] = None,
        bcc: Optional[list[str]] = None,
        cc: Optional[list[str]] = None,
        attachments: Optional[list[tuple[str | MIMEBase, Any, str] | None]] = None,
        headers: Optional[dict] = None,
        reply_to: Optional[list[str]] = None,
        alternatives: Optional[list] = None,
    ):
        super().__init__(
            to, subject, body, from_email, bcc, cc, attachments, headers, reply_to
        )
        self.alternatives = []
        if alternatives:
            for alternative in alternatives:
                self.attach_alternative(*alternative)

    def attach_alternative(self, content, mimetype) -> None:
        """Добавляет альтернативный вид письма"""
        self.alternatives.append((content, mimetype))

    def _create_message(
        self, message: SafeMIMEText
    ) -> SafeMIMEText | SafeMIMEMultipart:
        return self._create_attachments(self._create_alternatives(message))

    def _create_alternatives(
        self, message: SafeMIMEText | SafeMIMEMultipart
    ) -> SafeMIMEText | SafeMIMEMultipart:
        """Создаёт альтернативные представления письма в MIMEMultipart"""
        if self.alternatives:
            message_body = message
            message = SafeMIMEMultipart(
                _subtype=self.alternative_subtype, encoding=self.encoding
            )
            if self.body:
                message.attach(message_body)
            for alternative in self.alternatives:
                message.attach(self._create_mime_attachment(*alternative))

        return message
