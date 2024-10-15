from redis import Redis, RedisError

from src.core.config import settings
from src.logs.storage import LogStorageABC
from src.logs.storage.exceptions import LogStorageError
from src.logs.types import LOG_KIND


class RedisStorage(LogStorageABC):
    """Реализация хранения логов в Redis"""

    def __init__(self) -> None:
        db_num = 3 if settings.REDIS.LOG_DB is None else settings.REDIS.LOG_DB
        self.redis = Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            db=db_num,
        )
        self.name = "logs"

    def append(self, kind: LOG_KIND, value) -> int:
        try:
            return self.redis.rpush(f"{kind}_{self.name}", value)  # type: ignore[union-attr]
        except RedisError:
            raise LogStorageError

    def get(self, kind: LOG_KIND) -> list[bytes]:
        try:
            return self.redis.lrange(f"{kind}_{self.name}", 0, -1)  # type: ignore[union-attr]
        except RedisError:
            raise LogStorageError

    def clear(self) -> int:
        keys = self._get_keys()
        try:
            return self.redis.delete(*keys)  # type: ignore[union-attr]
        except RedisError:
            raise LogStorageError(None, keys)

    def _get_keys(self) -> list[bytes]:
        try:
            return self.redis.keys(f"*{self.name}")  # type: ignore[union-attr]
        except RedisError:
            raise LogStorageError
