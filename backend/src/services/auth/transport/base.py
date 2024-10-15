from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Response
from fastapi.security.base import SecurityBase

from src.typing import OpenAPIResponseType


class TransportLogoutNotSupportedError(Exception):
    pass


class TransportABC(ABC):
    scheme: SecurityBase

    @abstractmethod
    async def get_login_response(
        self, token: str, refresh_token: Optional[str] = None
    ) -> Response:
        """
        Формирует HTTPResponse для входа

        :param token: Токен пользователя
        :param refresh_token: Рефреш токен пользователя (в случае JWTStrategy)
        :return: Экземпляр Response
        """
        raise NotImplementedError

    @abstractmethod
    async def get_logout_response(self) -> Response:
        """
        Формирует HTTPResponse для выхода

        :return: Экземпляр Response
        """
        raise NotImplementedError

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        """Получить примеры ответов входа для OpenAPI"""
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        """Получить примеры ответов выхода для OpenAPI"""
        ...  # pragma: no cover
