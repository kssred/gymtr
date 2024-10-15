from abc import ABC, abstractmethod

from src.logs.types import LOG_KIND


class LogStorageABC(ABC):
    """Абстрактный класс для хранилища логов"""

    @abstractmethod
    def append(self, kind: LOG_KIND, value) -> int:
        """
        Добавить значение в хранилище логов

        :raises LogStorageError: Ошибка хранилища логов
        :return: Количество добавленных записей
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, kind: LOG_KIND) -> list[bytes]:
        """
        Получить все логи из хранилища

        :raises LogStorageError: Ошибка хранилища логов
        :return: Список всех найденных записей в байтах
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> int:
        """
        Очистить хранилище

        :raises LogStorageError: Ошибка хранилища логов
        :return: Количество удалённых записей
        """
        raise NotImplementedError
