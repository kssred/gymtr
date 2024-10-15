from fastapi import APIRouter, HTTPException, status

from src.api.v1.dependencies import CurrentUserDependency, UserServiceDependency
from src.api.v1.error import UserErrorCode
from src.api.v1.openapi.user import ME_GET_RESPONSES, ME_PATCH_RESPONSES
from src.schemas.user import UserReadSchema, UserUpdateSchema
from src.services.auth.exceptions import UserAlreadyExist
from src.utils.shortcuts import get_http_error_detail

router = APIRouter()


@router.get(
    "/me",
    response_model=UserReadSchema,
    summary="Информация о пользователе",
    operation_id="auth:get_current_user",
    responses=ME_GET_RESPONSES,
)
async def get_user(user: CurrentUserDependency):
    return user


@router.patch(
    "/me",
    response_model=UserReadSchema,
    summary="Изменить информацию о пользователе",
    operation_id="auth:update_current_user",
    responses=ME_PATCH_RESPONSES,
)
async def update_user(
    user_service: UserServiceDependency,
    user: CurrentUserDependency,
    user_data: UserUpdateSchema,
):
    try:
        updated_user = await user_service.update(user.id, user_data)
    except UserAlreadyExist as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_http_error_detail(
                code=UserErrorCode.USER_ALREADY_EXIST,
                reason=e.reason,
                error_fields=e.error_fields,
            ),
        )

    return updated_user
