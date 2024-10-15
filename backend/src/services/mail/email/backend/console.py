from collections.abc import Iterable
from sys import stdout
from threading import RLock
from typing import Union

from src.services.mail.email.backend import EmailBackendABC
from src.services.mail.email.message import EmailMessage


class EmailConsoleBackend(EmailBackendABC):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop("stream", stdout)
        self._lock = RLock()

        super().__init__(*args, **kwargs)

    def send_messages(
        self, messages: Union[list[EmailMessage], Iterable[EmailMessage]]
    ) -> int:
        if not messages:
            return 0

        sent_count = 0
        with self._lock:
            try:
                for message in messages:
                    self.write_message(message)
                    self.stream.flush()
                    sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e

        return sent_count

    def write_message(self, message: "EmailMessage") -> None:
        msg = message.mime_message()
        msg_data = msg.as_bytes()
        charset = (
            msg.get_charset().get_output_charset() if msg.get_charset() else "utf-8"
        )

        msg_data = msg_data.decode(charset)
        self.stream.write(f"{msg_data}\n")
        self.stream.write("-" * 79)
        self.stream.write("\n")

    def _close(self):
        pass

    def _open(self):
        pass
