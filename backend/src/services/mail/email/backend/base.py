from abc import ABC, abstractmethod
from typing import Iterable, Optional, Union

from src.services.mail.email.message import EmailMessage


class EmailBackendABC(ABC):
    """Абстрактный класс бэкенда отправки сообщений"""

    def __init__(self, fail_silently: bool = False, **kwargs):
        self.fail_silently = fail_silently

    @abstractmethod
    def send_messages(
        self, messages: Union[list[EmailMessage], Iterable[EmailMessage]]
    ) -> int:
        """
        Отправляет одно или несколько Email сообщений

        :param messages: Список из экземпляров EmailMessage
        :return int: Количество отправленных сообщений
        """
        raise NotImplementedError

    @abstractmethod
    def _open(self) -> Optional[bool]:
        """Открывает соединение"""
        raise NotImplementedError

    @abstractmethod
    def _close(self) -> None:
        """Закрывает соединение"""
        raise NotImplementedError

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()
