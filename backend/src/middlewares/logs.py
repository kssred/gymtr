from http import HTTPStatus
from logging import getLogger
from math import ceil
from time import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.logs.schemas import RequestJSONLogSchema

EMPTY_VALUE = ""

logger = getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов-ответов"""

    @staticmethod
    async def get_protocol(request: Request) -> str:
        protocol = str(request.scope.get("type", ""))
        http_version = str(request.scope.get("http_version", ""))

        if protocol.lower() == "http" and http_version:
            return f"{protocol.upper()}/{http_version}"
        return EMPTY_VALUE

    @staticmethod
    async def set_body(request: Request, body: bytes) -> None:
        async def receive() -> dict:
            return {"type": "http_request", "body": body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time()

        self.request_body = await self._get_request_body(request)
        server: tuple = request.get("host", ("localhost", 8000))
        self.request_headers = dict(request.headers.items())

        (
            response,
            self.response_headers,
            self.response_body,
            exception,
        ) = await self._get_response(request, call_next)

        self.duration = ceil((time() - start_time) * 1000)
        request_fields = await self._get_request_fields(request, response, server)

        message = (
            f'{"Ошибка" if exception else "Ответ"} '
            f"с кодом {response.status_code} "
            f'на запрос {request.method} "{str(request.url)}", '
            f"за {self.duration} мс"
        )

        if exception:
            logger.error(
                message,
                extra={"request_fields": request_fields},
                exc_info=exception,
            )

        return response

    async def _get_request_body(self, request: Request) -> str:
        try:
            # Необходимо, чтобы не перезатереть данные из body
            raw_request_body = await request.body()
            await self.set_body(request, raw_request_body)
            raw_request_body = await self.get_body(request)
            request_body = raw_request_body.decode()
        except Exception:
            request_body = EMPTY_VALUE

        return request_body

    async def _get_response(
        self, request: Request, call_next
    ) -> tuple[Response, dict, bytes, Optional[Exception]]:
        try:
            response = await call_next(request)
        except Exception as ex:
            exception = ex
            response_headers = {}
            response_body = bytes(HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode())

            response = Response(
                content=response_body,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR.real,
            )
        else:
            exception = None
            response_headers = dict(response.headers.items())
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return response, response_headers, response_body, exception

    async def _get_request_fields(
        self, request: Request, response: Response, server: tuple
    ):
        try:
            remote_ip: str = request.client[0]  # pyright: ignore [reportOptionalSubscript]
        except TypeError:
            remote_ip = request.get("x-forwarded-for", "")

        request_fields = RequestJSONLogSchema(
            request_uri=str(request.url),
            request_referer=self.request_headers.get("referer", EMPTY_VALUE),
            request_protocol=await self.get_protocol(request),
            request_method=request.method,
            request_path=request.url.path,
            request_host=f"{server[0]}:{server[1]}",
            request_size=int(self.request_headers.get("content-length", 0)),
            request_content_type=self.request_headers.get("content-type", EMPTY_VALUE),
            request_headers=self.request_headers,
            request_body=self.request_body,
            request_direction="in",
            remote_ip=remote_ip,
            response_status_code=response.status_code,
            response_size=int(self.response_headers.get("content-length", 0)),
            response_headers=self.response_headers,
            response_body=self.response_body.decode(),
            duration=self.duration,
        ).model_dump()

        return request_fields
