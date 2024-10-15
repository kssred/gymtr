from abc import ABC, abstractmethod
from typing import Any, TypeAlias, Union

from celery.result import AsyncResult

TASK_ID: TypeAlias = Union[str, int]
TASK: TypeAlias = Union[AsyncResult, Any]


class TaskServiceABC(ABC):
    @staticmethod
    @abstractmethod
    async def create_task(function, *args, **kwargs) -> TASK_ID:
        """
        Создать задачу для отложенного выполнения

        :param function: Функция, которая будет отложенно вызываться
        :param args: Позиционные аргументы для задачи
        :param kwargs: Именованные  аргументы для задачи
        :return: Id задачи
        """

        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def get_task(task_id: TASK_ID) -> TASK:
        """
        Получить задачу по её Id

        :param task_id: Id задачи
        :return: Объект задачи
        """
        raise NotImplementedError
