from src.exceptions import ProjectException


class MailServiceError(ProjectException):
    reason = "Ошибка сервиса рассылки"
