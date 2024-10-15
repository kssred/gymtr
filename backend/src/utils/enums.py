from enum import IntEnum
from inspect import signature
from typing import Callable


class FunctionProxy:
    """Позволяет обернуть функцию в объект"""

    def __init__(self, function: Callable):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def signature(self):
        return signature(self.function)


class SecondsTo(IntEnum):
    ONE_SECOND = 1
    ONE_MINUTE = 60
    ONE_HOUR = 60 * 60
    ONE_DAY = 60 * 60 * 24
    ONE_WEEK = 60 * 60 * 24 * 7


class BytesTo(IntEnum):
    ONE_KB = 2**10
    ONE_MB = 2**10 * 2**10
    ONE_GB = 2**10 * 2**10 * 2**10
