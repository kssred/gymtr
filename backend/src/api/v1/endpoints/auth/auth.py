from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from src.api.v1.dependencies import (
    RefreshUserDependency,
    UserServiceDependency,
)
from src.api.v1.error import AuthErrorCode, UserErrorCode
from src.api.v1.openapi.auth.auth import (
    LOGIN_POST_RESPONSES,
    REFRESH_GET_RESPONSES,
    REGISTER_POST_RESPONSES,
)
from src.schemas.user import UserCreateSchema, UserReadSchema
from src.services.auth.config import bearer_jwt_backend, cookie_transport
from src.services.auth.exceptions import InvalidPassword, UserAlreadyExist
from src.services.auth.strategy import StrategyABC
from src.utils.shortcuts import get_http_error_detail

router = APIRouter()

backend = bearer_jwt_backend

login_post_responses = {
    **LOGIN_POST_RESPONSES,
    **backend.transport.get_openapi_login_responses_success(),
}
refresh_get_responses = {
    **REFRESH_GET_RESPONSES,
    **backend.transport.get_openapi_login_responses_success(),
}


@router.post(
    "/register",
    response_model=UserReadSchema,
    summary="Регистрация пользователя",
    operation_id="auth:register_user",
    responses=REGISTER_POST_RESPONSES,
)
async def register_user(
    user_service: UserServiceDependency,
    data: UserCreateSchema,
):
    try:
        return await user_service.create(data)
    except InvalidPassword as e:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = AuthErrorCode.INVALID_PASSWORD
        reason = e.reason
        error_fields = ["password1"]
    except UserAlreadyExist as e:
        status_code = status.HTTP_409_CONFLICT
        error_code = UserErrorCode.USER_ALREADY_EXIST
        reason = e.reason
        error_fields = e.error_fields

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(
            code=error_code,
            reason=reason,
            error_fields=error_fields,
        ),
    )


@router.post(
    "/login",
    summary="Вход пользователя",
    operation_id="auth:login_user",
    responses=login_post_responses,
)
async def login(
    user_service: UserServiceDependency,
    credentials: OAuth2PasswordRequestForm = Depends(),
    strategy: StrategyABC = Depends(backend.get_strategy),
):
    user = await user_service.authenticate(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_http_error_detail(
                code=AuthErrorCode.BAD_CREDENTIALS,
                reason="Указан неверный email или пароль",
            ),
        )

    access_token, refresh_token = await strategy.write_token(user)
    response = await backend.transport.get_login_response(access_token, refresh_token)

    if refresh_token:
        response.set_cookie(
            key=cookie_transport.cookie_name,
            value=refresh_token,
            max_age=cookie_transport.cookie_max_age,
            path=cookie_transport.cookie_path,
            domain=cookie_transport.cookie_domain,
            secure=True,
            httponly=True,
            samesite="none",
        )

    return response


@router.get(
    "/token/refresh",
    summary="Обновить access token",
    operation_id="auth:refresh",
    responses=refresh_get_responses,
)
async def refresh_token(
    user: RefreshUserDependency,
    strategy: StrategyABC = Depends(bearer_jwt_backend.get_strategy),
):
    token, refresh_token = await strategy.write_token(user)
    response = await bearer_jwt_backend.transport.get_login_response(
        token, refresh_token
    )
    if refresh_token:
        response.set_cookie(
            key=cookie_transport.cookie_name,
            value=refresh_token,
            max_age=cookie_transport.cookie_max_age,
            path=cookie_transport.cookie_path,
            domain=cookie_transport.cookie_domain,
            secure=True,
            httponly=True,
            samesite="none",
        )
    return response


@router.get(
    "/logout",
    summary="Выход",
    operation_id="auth:logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout():
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key=cookie_transport.cookie_name)
    return response
