import os
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic_settings import BaseSettings as PyBaseSettings
from pydantic_settings import SettingsConfigDict

from src.utils.enums import BytesTo, SecondsTo

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def get_model_config(env_prefix: str = "") -> SettingsConfigDict:
    env_filename = get_env_filename_by_env_state()
    env_file = BASE_DIR / env_filename

    return SettingsConfigDict(env_file=env_file, env_prefix=env_prefix, extra="allow")


def get_env_filename_by_env_state() -> str:
    env_state = os.getenv("ENV_STATE")
    machine = os.getenv("MACHINE")

    if env_state == "TEST":
        env_filename = ".test.env"
    elif machine == "COMPOSE":
        env_filename = ".compose.env"
    else:
        env_filename = ".env"
    return env_filename


class SwaggerSettings(PyBaseSettings):
    deepLinking: bool = True
    displayOperationId: bool = True
    filter: Union[bool, str] = True
    persistAuthorization: bool = True


class EmailSettings(PyBaseSettings):
    FROM_EMAIL: str = "Gymtr <help@gymtr.ru>"
    HOST: Optional[str] = None
    PORT: Optional[str] = None
    USERNAME: Optional[str] = None
    PASSWORD: Optional[str] = None
    BACKEND: Optional[str] = None
    TIMEOUT: Optional[int] = 30
    USE_TLS: Optional[bool] = None
    USE_SSL: Optional[bool] = None
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None

    model_config = get_model_config("SMTP_")


class DatabaseSettings(PyBaseSettings):
    HOST: str = "localhost"
    PORT: str = "5432"
    NAME: str = "postgres"
    USERNAME: str = "postgres"
    PASSWORD: str = "postgres"

    @property
    def URL(self):
        return f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    model_config = get_model_config("DB_")


class RedisSettings(PyBaseSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    DATA_DB: int = 2
    LOG_DB: Optional[int] = None
    CACHE_DB: int = 4
    BACKEND: Optional[str] = None

    @property
    def URL(self):
        return f"redis://{self.HOST}:{self.PORT}"

    model_config = get_model_config("REDIS_")


class LogSettings(PyBaseSettings):
    LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    STORAGE_HANDLER: str = "src.logs.handlers.StorageHandler"
    STORAGE_PATH: str = "src.logs.storage.RedisStorage"
    DIR: Path = BASE_DIR / "logs"
    MAX_FILE_SIZE: int = BytesTo.ONE_MB * 10
    CHECK_TIMEOUT: int = SecondsTo.ONE_MINUTE * 30
    WRITER_PATH: str = "src.logs.writer.RotationFileWriter"


class AuthSettings(PyBaseSettings):
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: list[str] = ["Gymtr:auth"]
    JWT_ACCESS_TOKEN_LIFETIME: int = SecondsTo.ONE_HOUR
    JWT_REFRESH_TOKEN_LIFETIME: int = SecondsTo.ONE_WEEK * 2
    RESET_TOKEN_LIFETIME: int = SecondsTo.ONE_MINUTE * 15
    CONFIRM_TOKEN_LIFETIME: int = SecondsTo.ONE_HOUR
    CHANGE_TOKEN_LIFETIME: int = SecondsTo.ONE_HOUR
    SECRET: str
    COOKIE_NAME: str = "c_token"
    COOKIE_MAX_AGE: int = SecondsTo.ONE_HOUR
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    PASSWORD_VALIDATORS: list[str] = [
        "src.services.validators.password.MinLengthPasswordValidator",
        "src.services.validators.password.NumericPasswordValidator",
        "src.services.validators.password.CommonPasswordValidator",
    ]

    model_config = get_model_config("AUTH_")


class CacheSettings(PyBaseSettings):
    DEFAULT_EXPIRE: int = SecondsTo.ONE_MINUTE


class CORSSettings(PyBaseSettings):
    ALLOW_ORIGINS: list[str] = [
        "http://localhost",
        "https://localhost",
        "http://localhost:5500",
        "https://localhost:5500",
    ]


class BaseSettings(PyBaseSettings):
    BASE_DIR: Path = BASE_DIR
    PROJECT_NAME: str = "Gymtr"
    MEDIA_URL: Path = Path("/media/")
    ABSOLUTE_MEDIA_ROOT: Path = BASE_DIR / "media/"
    PROJECT_VERSION: str = "0.1"
    ENV_STATE: Optional[Literal["DEVELOP", "PRODUCTION", "TEST"]]
    DEBUG: bool = False

    SWAGGER: SwaggerSettings = SwaggerSettings()
    DB: DatabaseSettings = DatabaseSettings()
    REDIS: RedisSettings = RedisSettings()
    LOG: LogSettings = LogSettings()
    EMAIL: EmailSettings = EmailSettings()  # type: ignore
    AUTH: AuthSettings = AuthSettings()  # type: ignore
    CORS: CORSSettings = CORSSettings()
    CACHE: CacheSettings = CacheSettings()

    model_config = get_model_config("")
