from fastapi import APIRouter, HTTPException, status

from src.api.v1.dependencies import (
    CurrentUserDependency,
    UserServiceDependency,
    UserVerificatorDependency,
)
from src.api.v1.error import AuthErrorCode, MailErrorCode, UserErrorCode
from src.api.v1.openapi.auth.password import (
    PATCH_PASSWORD_RESET_RESPONSES,
    POST_PASSWORD_RESET_RESPONSES,
    PUT_PASSWORD_CHANGE_RESPONSES,
)
from src.schemas.user import (
    UserPasswordChangeSchema,
    UserPasswordResetRequestSchema,
    UserPasswordResetSchema,
)
from src.services.auth.exceptions import (
    InvalidPassword,
    PasswordMatch,
    PasswordMismatch,
    UserNotExist,
)
from src.services.auth.exceptions import (
    InvalidTokenError as AuthInvalidToken,
)
from src.services.mail.exceptions import MailServiceError
from src.utils.shortcuts import get_http_error_detail

router = APIRouter()


@router.put(
    "/change",
    summary="Сменить пароль",
    operation_id="auth:change_password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=PUT_PASSWORD_CHANGE_RESPONSES,
)
async def change_password(
    data: UserPasswordChangeSchema,
    user: CurrentUserDependency,
    user_service: UserServiceDependency,
):
    try:
        return await user_service.change_password(user, data)
    except (PasswordMatch, PasswordMismatch, InvalidPassword) as e:
        if isinstance(e, PasswordMatch):
            error_code = AuthErrorCode.USER_PASSWORD_MATCH
            error_fields = e.error_fields
        elif isinstance(e, PasswordMismatch):
            error_code = AuthErrorCode.USER_PASSWORD_MISMATCH
            error_fields = e.error_fields
        else:
            error_code = AuthErrorCode.INVALID_PASSWORD
            error_fields = None

        status_code = status.HTTP_409_CONFLICT
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(
            code=error_code, reason=reason, error_fields=error_fields
        ),
    )


@router.post(
    "/reset",
    summary="Отправить ссылку для восстановления пароля на email",
    operation_id="auth:reset_password_request",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=POST_PASSWORD_RESET_RESPONSES,
)
async def reset_password_request(
    data: UserPasswordResetRequestSchema,
    user_verificator: UserVerificatorDependency,
):
    try:
        return await user_verificator.reset_password_request(
            data.email, data.frontend_url
        )
    except UserNotExist as e:
        status_code = status.HTTP_404_NOT_FOUND
        error_code = UserErrorCode.USER_NOT_EXIST
        reason = e.reason
    except MailServiceError as e:
        status_code = status.HTTP_502_BAD_GATEWAY
        error_code = MailErrorCode.SEND_ERROR
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )


@router.patch(
    "/reset",
    summary="Восстановить пароль",
    operation_id="auth:reset_password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=PATCH_PASSWORD_RESET_RESPONSES,
)
async def reset_password(
    token: str,
    data: UserPasswordResetSchema,
    user_verificator: UserVerificatorDependency,
):
    try:
        return await user_verificator.reset_password(token, data.password)
    except UserNotExist as e:
        status_code = status.HTTP_404_NOT_FOUND
        error_code = UserErrorCode.USER_NOT_EXIST
        reason = e.reason
    except (AuthInvalidToken, InvalidPassword) as e:
        if isinstance(e, AuthInvalidToken):
            error_code = AuthErrorCode.BAD_TOKEN
        else:
            error_code = AuthErrorCode.INVALID_PASSWORD
        status_code = status.HTTP_409_CONFLICT
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )
