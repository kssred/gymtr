from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Literal, Optional, Sequence, TypeVar

from src.core.types import ID

MODEL = TypeVar("MODEL")


class RepositoryABC(Generic[MODEL, ID], ABC):
    @abstractmethod
    async def find_all(self) -> list[MODEL]:
        """
        Найти все записи

        :return: Список найденных записей
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id_: ID) -> MODEL:
        """
        Найти одну запись по её ID

        :param id_: Id записи
        :raises MultipleResultsFound: Найдено больше одной записи
        :raises NoResultFound: Не найдено ни одной записи
        :raises RepositoryException: Ошибка при получении
        :return: Найденная запись
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, **filters) -> MODEL:
        """
        Найти одну запись уникальным фильтрам

        :param filters: Kwargs для фильтрации
        :raises MultipleResultsFound: Найдено больше одной записи
        :raises NoResultFound: Не найдено ни одной записи
        :raises RepositoryException: Ошибка при получении
        :return: Найденная запись
        """
        raise NotImplementedError

    @abstractmethod
    async def get_or_none(self, **filters) -> Optional[MODEL]:
        """
        Найти одну запись уникальным фильтрам или ничего

        :param filters: Kwargs для фильтрации
        :raises RepositoryException: Ошибка при получении
        :return: Найденная запись или None
        """
        raise NotImplementedError

    @abstractmethod
    async def filter(self, **filters) -> list[MODEL]:
        """
        Отфильтровать записи

        :param filters: Kwargs для фильтрации
        :return: Список найденных записей
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, **filters) -> bool:
        """
        Проверяет есть ли такая запись

        :param filters: Kwargs для фильтрации
        :returns: True, если запись есть
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(
        self,
        data: Sequence[dict[str, Any]],
        on_conflict: Optional[Literal["do_nothing"]] = None,
        index_elements: Optional[Sequence[str]] = None,
        render_nulls: bool = False,
        **kwargs,
    ) -> None:
        """
        Создать несколько записей

        :param data: Список из данных для добавления
        :param on_conflict: Что делать при конфликте вставки
        :param index_elements: Колонки, по которым может произойти конфликт
        :param render_nulls: Обязательно ли проставлять не указанные поля в NULL
        :raises IntegrityError: Ошибка уникальности полей
        :raises RepositoryException: Ошибка при добавлении
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict[str, Any], **kwargs) -> MODEL:
        """
        Создать новую запись

        :param data: Данные для создания записи
        :raises IntegrityError: Ошибка уникальности полей
        :raises RepositoryException: Ошибка при добавлении
        :return: Созданная запись
        """
        raise NotImplementedError

    @abstractmethod
    async def create_or_update(
        self,
        data: Sequence[dict[str, Any]],
        index_elements: Sequence[str],
        returning: Optional[Sequence[str]] = None,
        render_nulls: bool = False,
        **kwargs,
    ) -> Sequence[MODEL]:
        """
        Создаёт или обновляет записи (UPSERT)

        :param data: Список из данных для добавления
        :param index_elements: Колонки, по которым может произойти конфликт
        :param returning: Список строк - названий колонок, которые необходимо вернуть (по умолчанию возвращается вся модель)
        :param render_nulls: Обязательно ли проставлять не указанные поля в NULL
        :raises IntegrityError: Ошибка уникальности полей
        :raises RepositoryException: Ошибка при добавлении
        :return: Список из созданных записей
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, record_id: ID, data: dict[str, Any], **kwargs) -> MODEL:
        """
        Обновить запись

        :param record_id: Id старой записи
        :param data: Данные для обновления записи
        :raises IntegrityError: Ошибка уникальности полей
        :raises NoResultFound: Не найдено ни одной записи для обновления
        :raises MultipleResultsFound: Найдено больше одной записи для обновления
        :raises RepositoryException: Ошибка при обновлении
        :return: Обновлённая запись
        """
        raise NotImplementedError

    @abstractmethod
    async def update_by_filters(self, data: dict[str, Any], **filters) -> list[MODEL]:
        """
        Обновить записи по фильтрам

        :param data: Данные для обновления записей
        :param filters: Фильтры для выборки записей под обновление
        :raises IntegrityError: Ошибка уникальности полей
        :raises RepositoryException: Ошибка при обновлении
        :return: Список из обновлённых записей
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, record_id: ID, **kwargs) -> int:
        """
        Удалить запись

        :param record_id: Id записи для удаления
        :raises NoResultFound: Не найдено записей для удаления
        :raises MultipleResultsFound:
        :return: Количество удалённых
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_delete_by_filter(self, **filters) -> int:
        """
        Удалить несколько записей по фильтрам

        :param filters: Фильтры для выборки записей под удаление
        :return: Количество удалённых
        """
        raise NotImplementedError

    @abstractmethod
    async def bulk_delete_by_ids(self, records_ids: list[ID]) -> int:
        """
        Удалить несколько записей по их Id

        :param records_ids: Список Id записей для удаления
        :return: Количество удалённых
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def check_connection(cls) -> None:
        """
        Проверяет подключение к базе данных

        :raises ConnectionError: Ошибка при подключении
        :return: None
        """
        raise NotImplementedError


class KeyValueRepositoryABC(Generic[MODEL], ABC):
    base_key: str

    @abstractmethod
    async def get(self, key: str) -> MODEL:
        """
        Получить запись по ключу

        :param key: Ключ записи
        :raises NoResultFound: Не найдено ни одной записи
        :return: Найденная запись
        """
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Проверяет есть ли такая запись

        :param key: Ключ записи
        :returns: True, если запись есть
        """
        raise NotImplementedError

    @abstractmethod
    async def filter(self, key_pattern: str) -> list[dict[str, MODEL]]:
        """
        Отфильтровать записи

        :param key_pattern: Паттерн, которому должны удовлетворять ключи
        :return: Список найденных записей
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, key: str, data: MODEL, **kwargs) -> MODEL:
        """
        Создать новую запись

        :param key: Ключ записи
        :param data: Данные для создания записи
        :raises IntegrityError: Ошибка уникальности полей
        :raises RepositoryException: Ошибка при добавлении
        :return: Созданная запись
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, key: str, data: dict[str, Any], fields: Iterable[str], **kwargs
    ) -> MODEL:
        """
        Обновить запись

        :param key: Ключ записи
        :param data: Данные для обновления записи
        :param fields: Итерируемый объект, с названиями полей для обновления
        :raises IntegrityError: Ошибка уникальности полей
        :raises NoResultFound: Не найдено ни одной записи
        :raises RepositoryException: Ошибка при обновлении
        :return: Обновлённая запись
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str, **kwargs) -> None:
        """
        Удалить запись

        :param key: Ключ записи
        :return: None
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def check_connection(cls) -> None:
        """
        Проверяет подключение к базе данных

        :raises ConnectionError: Ошибка при подключении
        :return: None
        """
        raise NotImplementedError
