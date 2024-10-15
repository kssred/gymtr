from src.exceptions import ProjectException


class EmailBackendError(ProjectException):
    reason = "Ошибка при отправке электронной почты"
