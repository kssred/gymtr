from logging import Handler, LogRecord

from src.core.config import settings
from src.logs.tasks import save_log_to_storage
from src.logs.types import LOG_KIND


class StorageHandler(Handler):
    """Logger Handler записывающий логи в переданной хранилище"""

    def __init__(self, with_celery: bool = True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.with_celery = with_celery

    def emit(self, record: LogRecord) -> None:
        formatted_record = self.formatter.format(record)  # type: ignore
        kind = get_record_kind(record)

        if self.with_celery:
            save_log_to_storage.delay(kind, formatted_record, settings.LOG.STORAGE_PATH)  # type: ignore
        else:
            save_log_to_storage(kind, formatted_record)


def get_record_kind(record: LogRecord) -> LOG_KIND:
    if "celery" in record.name:
        return "celery"

    if record.levelno >= 40:
        kind = "error"
    else:
        kind = "access"
    return kind
