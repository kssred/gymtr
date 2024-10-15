from decimal import Decimal
from typing import TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            Decimal: lambda v: f"{v:.2f}",
        },
    )


BASE_SCHEMA = TypeVar("BASE_SCHEMA", bound=BaseSchema)
