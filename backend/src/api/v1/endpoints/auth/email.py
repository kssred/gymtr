from fastapi import APIRouter, HTTPException, status

from src.api.v1.dependencies import (
    CurrentUserDependency,
    UserServiceDependency,
    UserVerificatorDependency,
)
from src.api.v1.error import AuthErrorCode, MailErrorCode, UserErrorCode
from src.api.v1.openapi.auth.email import (
    GET_EMAIL_CHANGE,
    GET_EMAIL_VERIFY_RESPONSES,
    POST_EMAIL_CHANGE,
    POST_EMAIL_VERIFY_RESPONSES,
)
from src.schemas.user import (
    UserEmailChangeSchema,
    UserEmailVerifyRequestSchema,
    UserReadSchema,
)
from src.services.auth.exceptions import InvalidTokenError as AuthInvalidToken
from src.services.auth.exceptions import UserAlreadyExist, UserAlreadyVerified
from src.services.mail.exceptions import MailServiceError
from src.utils.shortcuts import get_http_error_detail

router = APIRouter()


@router.post(
    "/change",
    summary="Оправить ссылку для подтверждения смены почты на новый email",
    operation_id="auth:change_email_request",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=POST_EMAIL_CHANGE,
)
async def change_email_request(
    data: UserEmailChangeSchema,
    user: CurrentUserDependency,
    user_service: UserServiceDependency,
):
    try:
        return await user_service.change_email_request(
            user, data.email, data.frontend_url
        )
    except UserAlreadyExist as e:
        status_code = status.HTTP_409_CONFLICT
        error_code = UserErrorCode.USER_ALREADY_EXIST
        reason = e.reason
    except MailServiceError as e:
        status_code = status.HTTP_502_BAD_GATEWAY
        error_code = MailErrorCode.SEND_ERROR
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )


@router.get(
    "/change",
    summary="Подтвердить смену email",
    operation_id="auth:change_email",
    response_model=UserReadSchema,
    responses=GET_EMAIL_CHANGE,
)
async def change_email(token: str, email: str, user_service: UserServiceDependency):
    try:
        return await user_service.change_email(token, email)
    except (UserAlreadyExist, AuthInvalidToken) as e:
        if isinstance(e, UserAlreadyExist):
            error_code = UserErrorCode.USER_ALREADY_EXIST
        else:
            error_code = AuthErrorCode.BAD_TOKEN
        status_code = status.HTTP_409_CONFLICT
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )


@router.post(
    "/verify",
    summary="Оправить ссылку для подтверждения email",
    operation_id="auth:verify_email_request",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=POST_EMAIL_VERIFY_RESPONSES,
)
async def verify_email_request(
    data: UserEmailVerifyRequestSchema,
    user: CurrentUserDependency,
    user_verificator: UserVerificatorDependency,
):
    try:
        return await user_verificator.verify_email_request(user, data.frontend_url)
    except UserAlreadyVerified as e:
        status_code = status.HTTP_409_CONFLICT
        error_code = AuthErrorCode.USER_ALREADY_VERIFIED
        reason = e.reason
    except MailServiceError as e:
        status_code = status.HTTP_502_BAD_GATEWAY
        error_code = MailErrorCode.SEND_ERROR
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )


@router.get(
    "/verify",
    summary="Подтвердить email",
    operation_id="auth:verify_email",
    response_model=UserReadSchema,
    responses=GET_EMAIL_VERIFY_RESPONSES,
)
async def verify_email(token: str, user_verificator: UserVerificatorDependency):
    try:
        return await user_verificator.verify_email(token)
    except AuthInvalidToken as e:
        error_code = AuthErrorCode.BAD_TOKEN
        status_code = status.HTTP_409_CONFLICT
        reason = e.reason

    raise HTTPException(
        status_code=status_code,
        detail=get_http_error_detail(code=error_code, reason=reason),
    )
