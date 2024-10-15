from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.responses import JSONResponse, Response

from src.schemas.base import BaseSchema
from src.typing import OpenAPIResponseType

from .base import TransportABC, TransportLogoutNotSupportedError


class BearerResponse(BaseSchema):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class BearerTransport(TransportABC):
    def __init__(self, token_url: str):
        self.scheme = OAuth2PasswordBearer(token_url, auto_error=True)

    async def get_login_response(
        self, token: str, refresh_token: Optional[str] = None
    ) -> Response:
        bearer_response = BearerResponse(
            access_token=token, refresh_token=refresh_token, token_type="bearer"
        )
        return JSONResponse(bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedError

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5M2Q0ZWI0Mi0yYTZjLTRmM"
                            "jMtODM0NS04ODQ5ZjY3YzM4YjgiLCJhdWQiOlsiTWFzdGVyc2theWE6YXV0aCJdLCJ0b2t"
                            "lbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4NzA1MDY2fQ.wGFja6xsuyVwLmHXpjH3s5O"
                            "CzxVXu6v8CPkZj4fTLxM",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5M2Q0ZWI0Mi0yYTZjLTRm"
                            "MjMtODM0NS04ODQ5ZjY3YzM4YjgiLCJhdWQiOlsiTWFzdGVyc2theWE6YXV0aCJdLCJ0b"
                            "2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwOTkxMTA2Nn0.jjclFgsBVrF6k7dbC5L"
                            "sYtIYzmq9yrKTPQ7LPyXIToU",
                            "token_type": "bearer",
                        }
                    }
                },
            }
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}
