from abc import ABC, abstractmethod
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from sys import getsizeof

from celery.utils.log import get_logger

from src.core.config import settings
from src.logs.types import LOG_KIND

logger = get_logger(__name__)


class LogWriterABC(ABC):
    @abstractmethod
    def write(self, kind: LOG_KIND, logs: list[bytes]) -> int:
        raise NotImplementedError


class FileWriterABC(LogWriterABC, ABC):
    def _write(self, file: Path, logs: list[bytes]) -> int:
        """Записывает логи в обычный файл"""
        with open(file, "a") as f:
            f.write("\n".join([log.decode() for log in logs]))

        return len(logs)

    def _write_json(self, file: Path, logs: list[bytes]) -> int:
        """Записывает логи в JSON файл"""
        file_text = file.read_text()

        if file_text.strip() == "":
            file_logs = []
        else:
            file_logs = loads(file_text)

        for log in logs:
            try:
                file_logs.insert(0, loads(log))
            except JSONDecodeError as e:
                logger.error("Ошибка при сериализации записи", exc_info=e)

        data = dumps(file_logs, ensure_ascii=False, indent=2)
        file.write_text(data)
        return len(logs)

    def rotate_file(self, file: Path, file_idx: int) -> Path:
        destination = f"{file.stem}.{file_idx}{file.suffix}"
        return file.parent / destination

    @abstractmethod
    def should_rollover(self, file: Path, logs: list[bytes]) -> bool:
        """Должна ли происходить замена файла"""
        raise NotImplementedError

    def _get_file(self, kind: LOG_KIND, logs: list[bytes]) -> tuple[Path, str]:
        """Получает файл с нужным расширением в зависимости от типа логов"""

        kind_dir = settings.LOG.DIR / kind
        kind_dir.mkdir(exist_ok=True)

        try:
            loads(logs[0])
        except Exception:
            file_extension = "error"
        else:
            file_extension = "json"

        file = kind_dir / f"{kind}.{file_extension}"
        file.touch()

        return file, file_extension


class RotationFileWriter(FileWriterABC):
    """
    Класс для записи логов в файлы

    :param file_size: Максимальный размер главного файла логов в байтах
    :param max_backups: Максимальное количество бэкапов предыдущих логов
    :param allow_compression: Разрешить сжатие прошлых файлов логов
    """

    def __init__(self, file_size: int, backup_count: int = 5) -> None:
        self.file_size = file_size
        self.backup_count = backup_count

    def write(self, kind: LOG_KIND, logs: list[bytes]) -> int:
        """Записывает список лог-записей в JSON файл"""
        if not logs:
            return 0

        file_path, file_extension = self._get_file(kind, logs)

        if self.should_rollover(file_path, logs):
            self._do_rollover(file_path)

        file_path.touch()

        if file_extension == "json":
            write_count = self._write_json(file_path, logs)
        else:
            write_count = self._write(file_path, logs)

        return write_count

    def _do_rollover(self, file: Path) -> None:
        """Переименовывает все файлы по номерам, самый последний - удаляет"""

        if not self.backup_count:
            return

        for i in range(self.backup_count - 1, 0, -1):
            source_file = self.rotate_file(file, i)
            destination_file = self.rotate_file(file, i + 1)

            if source_file.exists():
                destination_file.unlink(missing_ok=True)
                source_file.rename(destination_file)

        destination_file = self.rotate_file(file, 1)
        destination_file.unlink(missing_ok=True)

        file.rename(destination_file)

    def should_rollover(self, file: Path, logs: list[bytes]) -> bool:
        """Необходимо ли переименование файлов логов"""

        file_size = file.stat().st_size
        logs_size = getsizeof(logs)

        if file_size + logs_size > self.file_size:
            return True

        return False
