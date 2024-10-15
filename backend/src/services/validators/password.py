import gzip
from functools import cached_property
from os import PathLike
from pathlib import Path
from typing import Optional

from src.services.validators.base import ValidatorABC
from src.services.validators.exceptions import PasswordValidationError


class MinLengthPasswordValidator(ValidatorABC):
    """Проверяет, чтобы пароль был больше минимальной длины"""

    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, value: str):
        if len(value) <= self.min_length:
            raise PasswordValidationError(
                reason=f"Длина пароля должна быть больше {self.min_length} символов"
            )


class CommonPasswordValidator(ValidatorABC):
    """Проверяет, чтобы пароль не был в списке распространённых (./common-passwords.txt.gz)"""

    def __init__(self, password_list_path: Optional[PathLike] = None):
        if not password_list_path:
            password_list_path = self.default_password_list_path

        try:
            with gzip.open(password_list_path, "rt", encoding="utf-8") as file:
                self.passwords = {x.strip() for x in file}
        except OSError:
            with open(password_list_path, "r") as file:
                self.passwords = {x.strip() for x in file}

    def validate(self, value: str):
        if value.lower().strip() in self.passwords:
            raise PasswordValidationError(reason="Пароль слишком распространённый")

    @cached_property
    def default_password_list_path(self):
        return Path(__file__).resolve().parent / "common-passwords.txt.gz"


class NumericPasswordValidator(ValidatorABC):
    """Проверяет, чтобы пароль состоял не только из цифр"""

    def validate(self, value: str):
        if value.isdigit():
            raise PasswordValidationError(reason="Пароль состоит только из цифр")
