from abc import ABC, abstractmethod
from typing import Literal

from src.core.types.user import UserProtocol

TOKEN_KIND = Literal["RESET", "CONFIRM", "CHANGE"]


class UserTokenGeneratorABC(ABC):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def make_token(self, user: UserProtocol, kind: TOKEN_KIND) -> str:
        """
        Создаёт токен, основываясь на данных пользователя

        :param user: Пользователь
        :param kind: Тип токена
        :return: Токен в виде строки
        """
        raise NotImplementedError

    @abstractmethod
    def check_token(self, token: str, **kwargs) -> str:
        """
        Проверяет полученный токен для конкретного пользователя

        :param token: Токен для валидации
        :raises InvalidToken: Невалидный токен
        :return: ID пользователя
        """
        raise NotImplementedError
