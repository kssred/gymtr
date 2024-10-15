from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Coroutine,
    Generator,
    ParamSpec,
    TypedDict,
    TypeVar,
    Union,
)

PARAM = ParamSpec("PARAM")
RETURN_TYPE = TypeVar("RETURN_TYPE")


class EmptyDict(TypedDict):
    """Пустой словарь для использования в аннотациях"""


OpenAPIResponseType = dict[Union[int, str], dict[str, Any]]
DependencyCallable = Callable[
    ...,
    Union[
        RETURN_TYPE,
        Coroutine[None, None, RETURN_TYPE],
        AsyncGenerator[RETURN_TYPE, None],
        Generator[RETURN_TYPE, None, None],
        AsyncIterator[RETURN_TYPE],
    ],
]
