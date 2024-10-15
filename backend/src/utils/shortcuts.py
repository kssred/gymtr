from typing import Any, Optional, Union, overload
from uuid import UUID, uuid4

from fastapi.params import Query
from pydantic import BaseModel

from src.schemas.error import ErrorCodeReasonSchema
from src.utils.exceptions import InvalidID


def get_http_error_detail(
    code: str, reason: str, error_fields: Optional[list[str]] = None
) -> dict[str, Any]:
    """Получить словарь для описания HTTPException"""

    error = ErrorCodeReasonSchema(code=code, reason=reason, error_fields=error_fields)
    return error.model_dump()


def get_unique_filename(filename: str) -> str:
    """Получить уникальное имя с uuid4 вначале"""

    new_filename = f"{uuid4()}_{filename}"
    return new_filename


def dump_without_none(schema: BaseModel) -> dict[str, Any]:
    """Получить словарь из схемы с удалёнными `None` полями"""

    schema_dict = {}
    for param, value in schema.model_dump().items():
        if value:
            if isinstance(value, Query):
                continue

            schema_dict[param] = value

    return schema_dict


@overload
def parse_id(value: Any, type_: type[UUID]) -> UUID: ...


@overload
def parse_id(value: Any, type_: type[int]) -> int: ...


def parse_id(value: Any, type_: Union[type[UUID], type[int]]) -> Union[UUID, int]:
    """
    Разбирает value в корректное UUID

    :param value: Значение для разбора
    :raises UserInvalidID: Невалидный id пользователя
    :return: UUID
    """
    if isinstance(value, type_):
        return value
    try:
        return type_(value)
    except Exception as e:
        raise InvalidID from e
