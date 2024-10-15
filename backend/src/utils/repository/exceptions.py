from src.exceptions import ProjectException


class RepositoryException(ProjectException):
    reason = "Ошибка репозитория"


class ConnectionError(RepositoryException):
    reason = "Ошибка подключения к базе данных"


class NoResultFound(RepositoryException):
    reason = "Объект не найден, когда требовался один"


class MultipleResultsFound(RepositoryException):
    reason = "Найдено множество, когда требовался один"


class IntegrityError(RepositoryException):
    reason = "Ошибка уникальности поля"

    def __init__(self, *args, error_info: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_fields = self.get_error_fields(error_info)

    @staticmethod
    def get_error_fields(error_info: str) -> list[str]:
        start_idx = error_info.find(" (") + len(" (")
        end_idx = error_info.find(")=")
        fields = error_info[start_idx:end_idx].split(", ")
        return fields
