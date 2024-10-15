from base64 import b64decode, b64encode
from random import randint
from time import time
from typing import Iterable

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from src.core.config import settings
from src.core.types.user import UserProtocol

from .base import TOKEN_KIND, UserTokenGeneratorABC
from .exceptions import InvalidToken

SALT = get_random_bytes(16)


class CryptoUserTokenGenerator(UserTokenGeneratorABC):
    encryptor = AES
    encryptor_mode = AES.MODE_GCM

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._password = settings.AUTH.SECRET
        self._key = PBKDF2(self._password, SALT, dkLen=32)

    def make_token(self, user: UserProtocol, kind: TOKEN_KIND) -> str:
        payload_bytes = self._generate_payload(user, kind).encode()
        cipher = self.encryptor.new(self._key, self.encryptor_mode)  # type: ignore

        cipher_bytes, mac = cipher.encrypt_and_digest(payload_bytes)
        nonce = cipher.nonce

        result = self.b64encode([nonce, cipher_bytes, mac])

        return result

    def check_token(self, token: str, **kwargs) -> str:
        try:
            nonce, cipher_bytes, mac = self.b64decode(token)
        except ValueError:
            raise InvalidToken

        cipher = self.encryptor.new(self._key, self.encryptor_mode, nonce=nonce)  # type: ignore
        try:
            plaintext = cipher.decrypt_and_verify(cipher_bytes, mac).decode()
        except ValueError:
            raise InvalidToken

        user_id = self.validate_payload(plaintext)

        return user_id

    def validate_payload(self, token: str) -> str:
        """Валидирует payload"""

        user_id, kind, timestamp_str = token.split(":")

        timedelta = time() - float(timestamp_str)
        if timedelta > getattr(settings.AUTH, f"{kind}_TOKEN_LIFETIME"):
            raise InvalidToken(reason="Срок действия токена истёк")

        return user_id

    @staticmethod
    def b64encode(parts: Iterable, delimiter: str = ":") -> str:
        """Кодирует части в base64, удаляя знаки `=` в конце"""
        return delimiter.join(
            [b64encode(part).decode("utf-8").rstrip("=") for part in parts]
        )

    @staticmethod
    def b64decode(text: str, delimiter: str = ":") -> list[bytes]:
        """Декодирует из base64, учитывая отсутствие знаков `=` в конце"""
        return [
            b64decode(part + "=" * ((4 - len(part) % 4) % 4))
            for part in text.split(delimiter)
        ]

    @staticmethod
    def _generate_payload(user: UserProtocol, kind: str) -> str:
        timestamp = time()
        payload = f"{user.id}:{kind}:{timestamp}"
        return payload


user_token_generator = CryptoUserTokenGenerator()


def generate_numeric_token(length: int = 4) -> str:
    number = randint(int(f'1{"0" * (length - 1)}'), int(f'{"9" * length}'))
    return str(number)
