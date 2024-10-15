from datetime import datetime
from json import dumps
from logging import Formatter, LogRecord
from traceback import format_exception
from typing import Iterable

from src.core.config import settings
from src.logs.filters import PIIFilter
from src.logs.schemas import BaseJSONLogSchema


class JSONLogFormatter(Formatter):
    """
    Класс Formatter для записи логов в JSON формате

    :param pii_patterns: Паттерны ключей, значения которых необходимо заменить
    :param exclude_patterns: Паттерны ключей, значения которых не нужно хранить в лог-записях
    """

    def __init__(
        self,
        exclude_patterns: Iterable[str],
        pii_patterns: Iterable[str],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.pii_filter = PIIFilter(pii_patterns, exclude_patterns)

    def format(self, record: LogRecord, *args, **kwargs) -> str:
        """
        Преобразование записи в JSON формат

        :param record: Запись лога
        :return: Строка JSON формата
        """

        log_dict = self._format_log_record(record)
        return dumps(log_dict, ensure_ascii=False)

    def _format_log_record(self, record: LogRecord) -> dict:
        """
        Перевод записи лога в JSON формат с необходимыми полями

        :param record: Запись лога
        :return: Словарь с полями записи
        """

        now = (
            datetime.fromtimestamp(record.created)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        duration = record.duration if hasattr(record, "duration") else record.msecs

        json_log = BaseJSONLogSchema(
            thread=record.process,
            timestamp=now,
            level=record.levelno,
            level_name=record.levelname,
            message=record.getMessage(),
            source=record.name,
            duration=duration,
            app_name=settings.PROJECT_NAME,
            app_env=settings.ENV_STATE,
        )
        if record.exc_info:
            json_log.exceptions = format_exception(*record.exc_info)
        elif record.exc_text:
            json_log.exceptions = record.exc_text

        json_log_dict = json_log.model_dump(exclude_unset=True)

        if hasattr(record, "request_fields"):
            filtered_request_fields = self.pii_filter.replace(
                record.request_fields  # pyright: ignore [reportAttributeAccessIssue]
            )
            json_log_dict.update(filtered_request_fields)
        if hasattr(record, "data"):
            json_log_dict.update(
                {"data": record.data}  # pyright: ignore [reportAttributeAccessIssue]
            )

        return json_log_dict
