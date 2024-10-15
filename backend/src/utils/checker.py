import inspect
from typing import TypeVar

from fastapi import Form, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import File
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo

BM = TypeVar("BM", bound=BaseModel)


def as_form(cls: type[BM]) -> type[BM]:
    new_parameters = []

    for field_name, model_field in cls.model_fields.items():
        model_field: FieldInfo  # type: ignore

        if isinstance(model_field, File):
            default = File(model_field.default)
        else:
            default = Form(model_field.default)

        new_parameters.append(
            inspect.Parameter(
                model_field.alias if model_field.alias else field_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default,
                annotation=model_field.annotation,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    cls.__signature__ = sig
    return cls


class MultipartChecker:
    """Валидатор правильности входных данных для multipart/form-data"""

    def __init__(self, model: type[BaseModel]):
        self.model = model

    def __call__(self, data: str = Form(...)):
        try:
            return self.model.model_validate_json(data)
        except ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
