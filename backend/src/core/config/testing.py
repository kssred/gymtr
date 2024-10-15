from pathlib import Path
from typing import Optional

from src.core.config.base import EmailSettings, LogSettings, RedisSettings


class EmailSettingsTest(EmailSettings):
    BACKEND: Optional[str] = "src.services.mail.EmailLocmemBackend"


class LogSettingsTest(LogSettings):
    STORAGE_PATH: str = "src.logs.storage.LocMemLogStorage"
    DIR: Path = Path(__file__).resolve().parents[3] / "tests/logs"


class RedisSettingsTest(RedisSettings):
    DATA_DB: int = 15
    LOG_DB: Optional[int] = 15
    CACHE_DB: int = 15
    BACKEND: Optional[str] = "src.services.cache.InMemoryBackend"
