from dotenv import load_dotenv

from src.core.config.testing import (
    EmailSettingsTest,
    LogSettingsTest,
    RedisSettingsTest,
)

from .base import (
    BASE_DIR,
    BaseSettings,
    get_env_filename_by_env_state,
)
from .develop import AuthSettingsDev, EmailSettingsDev
from .production import EmailSettingsProd, LogSettingsProd


class SettingsFactory:
    def __init__(self):
        self.ENV_STATE = ""

    def get_settings(self) -> BaseSettings:
        env_filename = get_env_filename_by_env_state()
        env_file = BASE_DIR / env_filename
        load_dotenv(env_file)

        base_settings = BaseSettings()  # type: ignore
        self.ENV_STATE = base_settings.ENV_STATE

        self.set_by_environ(base_settings)

        return base_settings

    def set_by_environ(self, base_settings: BaseSettings):
        if self.ENV_STATE == "DEVELOP":
            base_settings.DEBUG = True
            base_settings.EMAIL = EmailSettingsDev()  # type: ignore
            base_settings.AUTH = AuthSettingsDev()  # type: ignore

        elif self.ENV_STATE == "TEST":
            base_settings.ABSOLUTE_MEDIA_ROOT = BASE_DIR / "tests/media"
            base_settings.DEBUG = False
            base_settings.EMAIL = EmailSettingsTest()  # type: ignore
            base_settings.LOG = LogSettingsTest()
            base_settings.REDIS = RedisSettingsTest()
        else:
            base_settings.DEBUG = False
            base_settings.EMAIL = EmailSettingsProd()  # type: ignore
            base_settings.LOG = LogSettingsProd()

        self._before_build(base_settings)

        return base_settings

    def _before_build(self, settings: BaseSettings):
        settings.LOG.DIR.mkdir(parents=True, exist_ok=True)


factory = SettingsFactory()
settings = factory.get_settings()
