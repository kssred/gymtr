from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from itertools import chain
from typing import (
    Any,
    Callable,
    Literal,
    NamedTuple,
    Optional,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
)

from six import string_types
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute

from src.utils.enums import FunctionProxy
from src.utils.repository.sqlalchemy.exceptions import BadFilterFormat

QT = TypeVar("QT")


class BooleanFunction(NamedTuple):
    key: str
    sqlalchemy_fn: Callable
    only_one_arg: bool


BOOLEAN_FUNCTIONS = [
    BooleanFunction("or", or_, False),
    BooleanFunction("and", and_, False),
    BooleanFunction("not", not_, True),
]

BOOLEAN_FUNCTIONS_NAMES = Literal["or", "and", "not"]


class FilterOperator(Enum):
    """Операторы фильтрации выраженные через sqlalchemy.func.<operator>"""

    is_null = FunctionProxy(lambda f: f.is_(None))
    is_not_null = FunctionProxy(lambda f: f.isnot(None))
    eq = FunctionProxy(lambda f, a: f == a)
    ne = FunctionProxy(lambda f, a: f != a)
    gt = FunctionProxy(lambda f, a: f > a)
    lt = FunctionProxy(lambda f, a: f < a)
    ge = FunctionProxy(lambda f, a: f >= a)
    le = FunctionProxy(lambda f, a: f <= a)
    like = FunctionProxy(lambda f, a: f.like(f"%{a}%"))
    ilike = FunctionProxy(lambda f, a: f.ilike(f"%{a}%"))
    not_ilike = FunctionProxy(lambda f, a: ~f.ilike(f"%{a}%"))
    in_ = FunctionProxy(lambda f, a: f.in_(a))
    not_in = FunctionProxy(lambda f, a: ~f.in_(a))
    overlap = FunctionProxy(lambda f, a: f.overlap(a))
    contains = FunctionProxy(lambda f, a: f.contains(a))
    contained_by = FunctionProxy(lambda f, a: f.contained_by(a))
    full_text = FunctionProxy(lambda f, a: f.bool_op("%")(a))


class FilterDict(TypedDict):
    model: type[DeclarativeBase]
    field: str
    operator: FilterOperator
    value: Optional[Any]


FILTER_SPEC_TYPE: TypeAlias = Union[
    list[FilterDict],
    dict[str, list[FilterDict]],
    list[dict[str, list[FilterDict]]],
    list[dict[str, list[dict[str, FilterDict]]]],
    FilterDict,
]


class Operator:
    def __init__(self, operator: Optional[Union[FilterOperator, FilterDict]] = None):
        if not operator:
            operator = FilterOperator.eq
        elif not isinstance(operator, FilterOperator):
            operator = operator.get("operator")

        self.operator = operator
        self.name = operator.name
        self.function = operator.value
        self.arity = len(self.function.signature.parameters)

    def __repr__(self) -> str:
        return self.operator.name


class Filter:
    """Фильтр для обычных функций"""

    def __init__(self, filter_spec: FilterDict):
        self.filter_spec = filter_spec
        self.operator = Operator(filter_spec.get("operator"))
        self.model = filter_spec["model"]
        self.field = filter_spec["field"]
        self.value = filter_spec.get("value")

        value_present = True if filter_spec.get("value", None) is not None else False
        if not value_present and self.operator.arity == 2:
            raise BadFilterFormat("`value` должно быть задано")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.model.__name__}.{self.field}.{self.operator}({self.value})>"

    def format_for_sqlalchemy(self, query):
        """Привести запрос в валидный для SQLAlchemy вид"""

        function = self.operator.function
        arity = self.operator.arity

        field_name = self.filter_spec["field"]
        field: InstrumentedAttribute = getattr(self.model, field_name)

        if arity == 1:
            return function(field)
        else:
            return function(field, self.value)


class BooleanFilter:
    """
    Фильтр для булевых функций

    :param function: Булева функция
    :param filters: Фильтры, на которые будет накладываться булева функция
    """

    def __init__(self, function: Callable, *filters: Union[Filter, BooleanFilter]):
        self.function = function
        self.filters = filters

    def format_for_sqlalchemy(self, query):
        """Привести запрос в валидный для SQLAlchemy вид"""

        return self.function(
            *[filter.format_for_sqlalchemy(query) for filter in self.filters]
        )


def apply_filters(
    query: QT,
    filter_spec: FILTER_SPEC_TYPE,
) -> QT:
    """
    Применить фильтры к запросу.

    :param query: Запрос через SQLAlchemy
    :param filter_spec: Данные для фильтрации

        ```
        filters = [
            FilterDict(model=FirstModel, operator=FilterOperator.eq, field="id", value=123),
            FilterDict(model=FirstModel, operator=FilterOperator.like, field="first_name", value"имя")
        ]
        filters = {
            "or": [
                FilterDict(model=FirstModel, operator=FilterOperator.eq, field="id", value=123),
                FilterDict(model=SecondModel, operator=FilterOperator.ilike, field="bio", value="Это")
            ]
        }
        filters = [
            "not": [{
                "or": [
                    FilterDict(model=FirstModel, operator=FilterOperator.is_not_null, field="name", value=None)
                    FilterDict(model=SecondModel, operator=FilterOperator.eq, field="name", value="Значение"
                ]
            }]
        ]
        ```
    :return: Запрос с применёнными фильтрами
    """

    filters = _build_filters(filter_spec)
    sqlalchemy_filters = [filter.format_for_sqlalchemy(query) for filter in filters]

    if sqlalchemy_filters:
        query = query.filter(*sqlalchemy_filters)  # type: ignore

    return query


def _is_filter_iterable(filter_spec: FILTER_SPEC_TYPE) -> bool:
    """Проверяет являются ли параметры итерабельными и не словарём/строкой"""

    return isinstance(filter_spec, Iterable) and not isinstance(
        filter_spec, (string_types, dict)
    )


def _check_bool_func(bool_func: BooleanFunction, func_args: list[FilterDict]) -> None:
    """Проверяет валидность булевой функции и её аргументов"""

    if not _is_filter_iterable(func_args):
        raise BadFilterFormat(f"{bool_func.key} значение должно быть итерируемым")

    if bool_func.only_one_arg and len(func_args) != 1:
        raise BadFilterFormat(f"{bool_func.key} должно иметь один аргумент")

    if not bool_func.only_one_arg and len(func_args) < 1:
        raise BadFilterFormat(f"{bool_func.key} должно иметь хотя бы 1 аргумент")


def _build_filters(filter_spec: FILTER_SPEC_TYPE) -> list[Union[Filter, BooleanFilter]]:
    """Строит экземпляры классов Filter"""

    if _is_filter_iterable(filter_spec):
        filters = []
        for item in filter_spec:
            try:
                filters.append(_build_filters(item))  # type: ignore
            except BadFilterFormat:
                continue
        return list(chain.from_iterable(filters))

    if isinstance(filter_spec, dict):
        for bool_func in BOOLEAN_FUNCTIONS:
            if bool_func.key in filter_spec:
                func_args = filter_spec[bool_func.key]
                _check_bool_func(bool_func, func_args)

                filters = _build_filters(func_args)

                return [BooleanFilter(bool_func.sqlalchemy_fn, *filters)]

    return [Filter(filter_spec)]  # type: ignore
