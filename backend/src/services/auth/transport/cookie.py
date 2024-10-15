from typing import Literal, Optional

from fastapi import Response, status
from fastapi.security import APIKeyCookie

from src.core.config import settings
from src.typing import OpenAPIResponseType

from .base import TransportABC


class CookieTransport(TransportABC):
    def __init__(
        self,
        cookie_name: str = "c_token",
        cookie_max_age: Optional[int] = None,
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        self.cookie_name = cookie_name
        self.cookie_max_age = (
            cookie_max_age
            if cookie_max_age
            else settings.AUTH.JWT_REFRESH_TOKEN_LIFETIME
        )
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite: Literal["lax", "strict", "none"] = cookie_samesite
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

    async def get_login_response(
        self, token: str, refresh_token: Optional[str] = None
    ) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._set_login_cookie(response, token, refresh_token)

    async def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self._set_logout_cookie(response)

    def _set_login_cookie(
        self, response: Response, token: str, refresh_token: Optional[str] = None
    ) -> Response:
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    def _set_logout_cookie(self, response: Response) -> Response:
        response.delete_cookie(
            key=self.cookie_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {status.HTTP_204_NO_CONTENT: {"model": None}}

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {status.HTTP_204_NO_CONTENT: {"model": None}}
