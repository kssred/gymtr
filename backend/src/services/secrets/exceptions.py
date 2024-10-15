from src.exceptions import ProjectException


class SecretServiceError(ProjectException):
    reason = "Ошибка сервиса работы с секретами"


class TokenGeneratorError(SecretServiceError):
    reason = "Ошибка генератора токенов"


class InvalidToken(TokenGeneratorError):
    reason = "Невалидный токен"
