from typing import Any, Optional

from celery.utils.log import get_logger

from src.core.celery import celery_app
from src.core.config import settings
from src.logs.reader import read_logs_from_storage
from src.logs.storage import LogStorageABC
from src.logs.storage.exceptions import LogStorageError
from src.logs.types import LOG_KIND
from src.logs.writer import LogWriterABC
from src.utils.loading import import_string

logger = get_logger(__name__)


@celery_app.task(name="log-save-storage")
def save_log_to_storage(
    kind: LOG_KIND, formatted_record: str, storage_path: Optional[str] = None
):
    """Сохраняет лог-запись в Storage"""

    if storage_path is None:
        storage_path = settings.LOG.STORAGE_PATH

    storage_class = import_string(storage_path)
    storage: LogStorageABC = storage_class()
    try:
        storage.append(kind, formatted_record)
    except LogStorageError as e:
        logger.error(e.reason, exc_info=e)


@celery_app.task(name="log-write-file")
def write_logs(writer_path: str, writer_kwargs: Optional[dict[str, Any]]):
    """Записывает хранящиеся лог-записи из Storage в файл"""

    writer_class = import_string(writer_path)

    if not writer_kwargs:
        writer_kwargs = {}

    log_writer: LogWriterABC = writer_class(**writer_kwargs)
    storage_path = settings.LOG.STORAGE_PATH
    storage: LogStorageABC = import_string(storage_path)()

    logs = read_logs_from_storage(storage)

    write_count = 0
    for kind, values in logs.items():
        count = log_writer.write(kind, values)
        write_count += count

    storage.clear()

    return write_count
