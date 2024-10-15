from collections.abc import Iterable
from copy import deepcopy
from typing import Optional, Union

from src.services import mail
from src.services.mail.email.backend import EmailBackendABC
from src.services.mail.email.message import EmailMessage


class EmailLocmemBackend(EmailBackendABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(mail, "email_outbox"):
            mail.email_outbox = []

    def send_messages(
        self, messages: Union[list[EmailMessage], Iterable[EmailMessage]]
    ) -> int:
        msg_count = 0
        for message in messages:
            message.mime_message()
            mail.email_outbox.append(deepcopy(message))
            msg_count += 1
        return msg_count

    def _open(self) -> Optional[bool]:
        pass

    def _close(self) -> None:
        pass
