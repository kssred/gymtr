from src.utils.repository.exceptions import RepositoryException


class BadFilterFormat(RepositoryException):
    reason = "Неверный формат фильтра"


class EmptyFilterValue(BadFilterFormat):
    reason = "Пустое значение value"


class BadLoadFormat(RepositoryException):
    reason = "Неверный формат для загрузки полей"


class BadSortFormat(RepositoryException):
    reason = "Неверный формат для сортировки"
