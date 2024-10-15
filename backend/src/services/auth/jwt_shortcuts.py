from datetime import UTC, datetime, timedelta
from typing import Any, Optional, Union

import jwt
from pydantic import SecretStr

from src.core.config import settings

SecretType = Union[str, SecretStr]


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    secret: SecretType,
    lifetime_seconds: Optional[int] = None,
    algorithm: str = settings.AUTH.JWT_ALGORITHM,
) -> str:
    """
    Генерирует JWT token

    :param data: Данные, которые подставляются в JWT.payload
    :param secret: Секретная строка
    :param lifetime_seconds: Время жизни токена в секундах
    :param algorithm: Алгоритм формирования токена
    :return: Строка - токен
    """
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(UTC) + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType,
    audience: list[str],
    algorithms: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Извлекает payload из JWT токена

    :param encoded_jwt: Закодированный JWT
    :param secret: Секретная строка
    :param audience:
    :param algorithms: Список алгоритмов
    :return: Словарь, содержащийся в payload токена
    """
    if not algorithms:
        algorithms = [settings.AUTH.JWT_ALGORITHM]

    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
