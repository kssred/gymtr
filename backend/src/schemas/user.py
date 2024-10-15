from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, HttpUrl

from src.core.types.user import GenderType
from src.schemas.base import BaseSchema


class UserReadSchema(BaseSchema):
    id: UUID
    first_name: str
    email: Optional[EmailStr]
    gender: GenderType
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserCreateSchema(BaseSchema):
    first_name: str
    email: str
    password: str
    gender: GenderType


class UserUpdateSchema(BaseSchema):
    first_name: Optional[str] = Field(None, max_length=100)
    gender: GenderType


class UserPasswordChangeSchema(BaseSchema):
    old_password: str
    new_password: str


class UserEmailChangeSchema(BaseSchema):
    email: EmailStr
    frontend_url: HttpUrl


class UserLoginSchema(BaseSchema):
    email: str
    password: str


class PasswordValidateSchema(BaseSchema):
    password: str


class TokenRefreshSchema(BaseSchema):
    refresh_token: str


class UserEmailVerifyRequestSchema(BaseSchema):
    frontend_url: HttpUrl


class UserEmailVerifySchema(BaseSchema):
    confirm_token: str


class UserPasswordResetRequestSchema(BaseSchema):
    email: EmailStr
    frontend_url: HttpUrl


class UserPasswordResetSchema(BaseSchema):
    password: str
