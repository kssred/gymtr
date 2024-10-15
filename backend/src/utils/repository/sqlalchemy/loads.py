from typing import TypedDict, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase, Load

QT = TypeVar("QT", bound=tuple)


class LoadDict(TypedDict):
    model: type[DeclarativeBase]
    fields: list[str]


class LoadOnly:
    def __init__(self, load_spec: LoadDict) -> None:
        self.load_spec = load_spec
        self.field_names = load_spec["fields"]

    def format_to_sqlalchemy(self) -> Load:
        model = self.load_spec["model"]
        return Load(model).load_only(
            *[getattr(model, field_name) for field_name in self.field_names]
        )


def apply_loads(query: Select[QT], load_spec: list[LoadDict]) -> Select[QT]:
    """
    Применить загрузку нужных полей

    :param query: Запрос через SQLAlchemy
    :param load_spec: Данные для загрузки полей

        ```
        load_spec = [
            LoadDict(model=SmthModel, fields=["id", "name"])
        ]
        ```
    :return: Запрос с применёнными заданными полями для загрузки
    """

    loads = [LoadOnly(item) for item in load_spec]
    sqlalchemy_loads = [load.format_to_sqlalchemy() for load in loads]

    if sqlalchemy_loads:
        query = query.options(*sqlalchemy_loads)

    return query
