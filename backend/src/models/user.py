from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from src.core.types.user.gender import GenderType
from src.database import BaseModel
from src.models.types import created_at, str_50, updated_at, uuid_pk


class UserModel(BaseModel):
    __tablename__ = "user"

    id: Mapped[uuid_pk]
    first_name: Mapped[str_50] = mapped_column(comment="Имя")
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, comment="Email адрес"
    )
    gender: Mapped[GenderType] = mapped_column(comment="Пол пользователя")
    hashed_password: Mapped[str] = mapped_column(String(1024), comment="Захешированный пароль")
    is_active: Mapped[bool] = mapped_column(server_default=expression.true(), comment="Активен?")
    is_verified: Mapped[bool] = mapped_column(server_default=expression.false(), comment="Подтверждён?")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
