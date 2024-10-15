from abc import ABC, abstractmethod
from typing import Optional

from passlib import pwd
from passlib.context import CryptContext

from src.services.auth.exceptions import InvalidPassword


class PasswordHelperABC(ABC):
    @abstractmethod
    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Optional[str]]:
        """
        Проверяет совпадает ли исходный пароль с захешированным и обновляет хеш пароля, если это необходимо

        :param plain_password: Исходный пароль
        :param hashed_password: Хеш пароля
        :return: 3 возможных случая
        * (False, None) - пароли не совпали
        * (True, None) - пароли совпали, хеш не требуется обновлять
        * (True, str) - пароли совпали, но текущий хеш необходимо обновить
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Хеширует исходный пароль

        :param password: Пароль, хеш которого надо получить
        :return: захешированный пароль
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def generate(self, length: int = 10) -> str:
        """
        Генерирует исходный пароль (не захешированный)

        :return: Сгенерированный пароль
        """
        raise NotImplementedError  # pragma: no cover


class PasslibPasswordHelper(PasswordHelperABC):
    def __init__(self, context: Optional[CryptContext] = None):
        if not context:
            self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            self.context = context

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Optional[str]]:
        return self.context.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        if not password:
            raise InvalidPassword("Пароль не может быть пустым")

        return self.context.hash(password)

    def generate(self, length: int = 10) -> str:
        return pwd.genword(length=length)


passlib_password_helper = PasslibPasswordHelper()
