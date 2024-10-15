from typing import Optional

from src.schemas.base import BaseSchema


class ErrorSchema(BaseSchema):
    detail: "ErrorCodeReasonSchema"


class ErrorCodeReasonSchema(BaseSchema):
    code: str
    reason: str
    error_fields: Optional[list[str]]
