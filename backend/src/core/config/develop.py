from typing import Optional

from src.core.config.base import AuthSettings, EmailSettings
from src.utils.enums import SecondsTo


class EmailSettingsDev(EmailSettings):
    BACKEND: Optional[str] = "src.services.mail.EmailSMTPBackend"
    USE_SSL: Optional[bool] = True
    # BACKEND: Optional[str] = "src.services.mail.EmailConsoleBackend"


class AuthSettingsDev(AuthSettings):
    JWT_ACCESS_TOKEN_LIFETIME: int = SecondsTo.ONE_WEEK * 2
    PASSWORD_VALIDATORS: list[str] = []
