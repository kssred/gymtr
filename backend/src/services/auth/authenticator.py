import re
from inspect import Parameter, Signature
from typing import Callable, Optional, Sequence, cast
from uuid import UUID

from fastapi import Depends, HTTPException, status
from makefun import with_signature

from src.api.v1.error import AuthErrorCode, UserErrorCode
from src.core.types.user import UserProtocol
from src.services.auth import UserService, get_user_service
from src.services.auth.backend import AuthenticationBackend
from src.services.auth.exceptions import UserNotExist
from src.services.auth.strategy import StrategyABC
from src.utils.shortcuts import get_http_error_detail, parse_id

INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


class DuplicateBackendNamesError(Exception):
    pass


def name_to_variable_name(name: str) -> str:
    """Приводит название бэкенда в корректную строку"""
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


def name_to_strategy_variable_name(name: str) -> str:
    """Приводит название стратегии в корректную строку"""
    return f"strategy_{name_to_variable_name(name)}"


class Authenticator:
    def __init__(self, backends: Sequence[AuthenticationBackend]):
        self.backends = backends

    def current_user_token(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        refresh: bool = False,
    ):
        """
        Возвращает DependencyCallable для получения текущего пользователя с токеном

        :param optional: Если `True`, то возвращается `None` в случае не нахождения пользователя
        или неудовлетворения другим требованиям.
        Если `False`, возбуждает `401 Unauthorized`
        :param active: Если `True` возбуждает `401 Unauthorized` в случае, если пользователь не активный
        :param verified: Если `True` возбуждает `403 Forbidden` в случае, если пользователь не верифицирован
        :param refresh: Если `True` получает пользователя по refresh токену
        :raises HTTPException:
        :return: DependencyCallable
        """
        signature = self._get_dependency_signature()

        @with_signature(signature)
        async def current_user_token_dependency(*args, **kwargs):
            return await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                refresh=refresh,
                **kwargs,
            )

        return current_user_token_dependency

    def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        refresh: bool = False,
    ):
        """
        Возвращает DependencyCallable для получения текущего пользователя

        :param optional: Если `True`, то возвращается `None` в случае не нахождения пользователя
        или неудовлетворения другим требованиям.
        Если `False`, возбуждает `401 Unauthorized`
        :param active: Если `True` возбуждает `401 Unauthorized` в случае, если пользователь не активный
        :param verified: Если `True` возбуждает `403 Forbidden` в случае, если пользователь не верифицирован
        :param refresh: Если `True` получает пользователя по refresh токену
        :raises HTTPException:
        :return: DependencyCallable для получения текущего пользователя
        """

        signature = self._get_dependency_signature()

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                refresh=refresh,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(
        self,
        *args,
        optional: bool,
        active: bool,
        verified: bool,
        refresh: bool,
        user_service: UserService,
        **kwargs,
    ) -> tuple[Optional[UserProtocol], Optional[str]]:
        """
        Проводит аутентификацию пользователя

        :param args:
        :param optional:
        :param active:
        :param verified:
        :param kwargs:
        :return: Кортеж из объекта пользователя и его токена
        """

        user: Optional[UserProtocol] = None
        token: Optional[str] = None
        payload: Optional[dict] = None

        for backend in self.backends:
            token = kwargs[name_to_variable_name(backend.name)]
            strategy: StrategyABC = kwargs[name_to_strategy_variable_name(backend.name)]
            if token is not None:
                payload = await strategy.read_token(token, refresh)
                if payload:
                    user_id = payload.get("sub")
                    try:
                        parsed_id = parse_id(user_id, UUID)
                        user = await user_service.get_by_id(parsed_id)
                    except UserNotExist:
                        continue
                    if user:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        error_info = (UserErrorCode.USER_NOT_EXIST, "Пользователь не найден")
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                user = None
                status_code = status.HTTP_401_UNAUTHORIZED
            elif verified and not user.is_verified:
                user = None
                error_info = (
                    AuthErrorCode.USER_NOT_VERIFIED,
                    "Пользователь не подтверждён",
                )
        else:
            if token and not payload:
                error_info = (
                    AuthErrorCode.BAD_TOKEN,
                    "Невалидный или просроченный токен",
                )

        if not user and not optional:
            raise HTTPException(status_code, detail=get_http_error_detail(*error_info))

        return user, token

    def _get_dependency_signature(self) -> Signature:
        try:
            parameters: list[Parameter] = [
                Parameter(
                    name="user_service",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(get_user_service),
                )
            ]
            for backend in self.backends:
                parameters += [
                    Parameter(
                        name=name_to_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(cast(Callable, backend.transport.scheme)),
                    ),
                    Parameter(
                        name=name_to_strategy_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(backend.get_strategy),
                    ),
                ]
            return Signature(parameters)
        except ValueError:
            raise DuplicateBackendNamesError
