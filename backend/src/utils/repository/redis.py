from json import dumps, loads
from typing import Any, Iterable, NamedTuple, Type, TypeVar

from redis import RedisError
from redis.asyncio import Redis

from src.core.config import settings
from src.utils.repository import KeyValueRepositoryABC
from src.utils.repository.exceptions import NoResultFound, RepositoryException

T = TypeVar("T", bound=NamedTuple)


class RedisRepository(KeyValueRepositoryABC[T]):
    base_key: str
    model: Type[T]

    def __init__(self) -> None:
        self.redis = Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            db=settings.REDIS.DATA_DB,
        )

    async def get(self, key: str) -> T:
        result = await self.redis.get(f"{self.base_key}:{key}")
        if result is None:
            raise NoResultFound

        result_dict: Iterable = loads(result)
        return self.model(**result_dict)  # type: ignore

    async def exists(self, key: str) -> bool:
        try:
            await self.get(key)
        except NoResultFound:
            return False

        return True

    async def filter(self, key_pattern: str) -> list[dict[str, T]]:
        keys = await self.redis.keys(f"{self.base_key}:{key_pattern}")
        if len(keys) == 0:
            raise NoResultFound
        values = await self.redis.mget(*keys)
        result = []
        for key, values in zip(keys, values):
            dict_values: Iterable = loads(values.decode())
            result.append({key.decode(): self.model(**dict_values)})  # type: ignore
        return result

    async def create(self, key: str, data: T, **kwargs) -> T:
        ex = kwargs.get("ex")

        value_str = dumps(data._asdict())
        try:
            await self.redis.set(f"{self.base_key}:{key}", value_str, ex=ex)
        except RedisError:
            raise RepositoryException("Ошибка при добавлении")

        return data

    async def update(
        self, key: str, data: dict[str, Any], fields: Iterable[str], **kwargs
    ) -> T:
        ex = kwargs.get("ex")

        value_str = await self.redis.get(f"{self.base_key}:{key}")
        value_dict = loads(value_str)

        for field_name in fields:
            value_dict[field_name] = data.get(field_name)

        updated_data = dumps(value_dict)

        try:
            await self.redis.set(f"{self.base_key}:{key}", updated_data, ex)
        except RedisError:
            raise RepositoryException("Ошибка при обновлении")

        return self.model(**value_dict)  # type: ignore

    async def delete(self, key: str, **kwargs) -> None:
        try:
            await self.redis.delete(f"{self.base_key}:{key}")
        except RedisError:
            raise RepositoryException("Ошибка при удалении")

    @classmethod
    async def check_connection(cls) -> None:
        redis = Redis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, db=0)
        await redis.ping()
