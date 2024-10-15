from typing import Union, get_args

from celery.utils.log import get_logger

from src.logs.storage import LogStorageABC
from src.logs.storage.exceptions import LogStorageError
from src.logs.types import LOG_KIND
from src.utils.loading import import_string

logger = get_logger(__name__)


def read_logs_from_storage(
    storage: Union[str, LogStorageABC],  # pyright: ignore [reportRedeclaration]
) -> dict[LOG_KIND, list[bytes]]:
    """Прочитать лог-записи из переданного хранилища"""

    if isinstance(storage, str):
        storage_class = import_string(storage)
        storage: LogStorageABC = storage_class()

    logs = {}
    for kind in get_args(LOG_KIND):
        try:
            kind_logs = storage.get(kind)
        except LogStorageError as e:
            logger.error(e.reason, exc_info=e)
        else:
            logs[kind] = kind_logs

    return logs
