from src.exceptions import ProjectException


class ValidatorException(ProjectException):
    reason = "Ошибка валидации"


class PasswordValidationError(ProjectException):
    reason = "Пароль не валиден"
