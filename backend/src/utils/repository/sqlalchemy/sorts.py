from typing import Literal, Optional, TypedDict, TypeVar, Union

from sqlalchemy import Select, asc, desc
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute

from .exceptions import BadSortFormat

QT = TypeVar("QT", bound=tuple)

SORT_ASCENDING = "asc"
SORT_DESCENDING = "desc"


class SortDict(TypedDict):
    model: Optional[type[DeclarativeBase]]
    field: str
    direction: Literal["asc", "desc"]
    nulls: Optional[Literal["last", "first"]]


class Sort:
    def __init__(self, sort_spec: SortDict):
        self.sort_spec = sort_spec

        try:
            field_name = sort_spec["field"]
            direction = sort_spec["direction"]
        except KeyError:
            raise BadSortFormat("`field` и `direction` обязательные атрибуты")

        if direction not in [SORT_ASCENDING, SORT_DESCENDING]:
            raise BadSortFormat(f"Направление {direction} не валидное")

        self.model = sort_spec.get("model")
        self.field_name = field_name
        self.direction = direction
        self.nulls = sort_spec.get("nulls", "last")

    def get_named_models(self):
        if "model" in self.sort_spec:
            return {self.sort_spec["model"]}
        return set()

    def format_for_sqlalchemy(self, query: Select):
        direction = self.direction
        field_name = self.field_name

        if self.model:
            field: Union[str, InstrumentedAttribute] = getattr(self.model, field_name)
        else:
            field = field_name

        if direction == SORT_DESCENDING:
            sort_fnc = desc(field)
        else:
            sort_fnc = asc(field)

        if self.nulls == "last":
            return sort_fnc.nullslast()
        elif self.nulls == "first":
            return sort_fnc.nullsfirst()
        else:
            return sort_fnc


def get_named_models(sorts):
    models = set()
    for sort in sorts:
        models.update(sort.get_named_models())
    return models


def apply_sorts(query: Select[QT], sort_spec: list[SortDict]) -> Select[QT]:
    """
    Применить сортировку

    :param query: Запрос через SQLAlchemy
    :param load_spec: Данные для загрузки полей

        ```
        load_spec = [
            SortDict(model=SmthModel, field="name", direction="asc", nulls="last")
        ]
        ```
    :return: Запрос с применённой сортировкой
    """

    sorts = [Sort(item) for item in sort_spec]

    sqlalchemy_sorts = [sort.format_for_sqlalchemy(query) for sort in sorts]

    if sqlalchemy_sorts:
        query = query.order_by(*sqlalchemy_sorts)

    return query
