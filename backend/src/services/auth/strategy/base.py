from abc import ABC, abstractmethod
from typing import Optional

from src.core.types.user import UserProtocol


class StrategyDestroyNotSupportedError(Exception):
    pass


class StrategyABC(ABC):
    @abstractmethod
    async def read_token(
        self,
        token: Optional[str],
        refresh: bool,
    ) -> Optional[dict]:
        """
        Получает данные из токена

        :param token: Токен
        :param refresh: Если `True` передан refresh токен
        :return: Пользователь
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def write_token(
        self, user: UserProtocol, **kwargs
    ) -> tuple[str, Optional[str]]:
        """
        Создаёт токен для пользователя

        :param user: Пользователь
        :return: Строка - токен
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def destroy_token(self, token: str, user: UserProtocol) -> None:
        """
        Удаляет токен для пользователя

        :param token: Токен
        :param user: Соответствующий токену пользователь
        :return: None
        """
        raise NotImplementedError  # pragma: no cover
