from src.exceptions import ProjectException


class LogStorageError(ProjectException):
    reason = "Ошибка хранилища логов"
