from src.exceptions import ErrorFieldsMixin, ProjectException


class UserServiceError(ProjectException):
    reason = "Ошибка работы сервиса с пользователями"


class UserNotExist(UserServiceError):
    reason = "Пользователь не найден"


class UserAlreadyExist(ErrorFieldsMixin, UserServiceError):
    reason = "Такой пользователь уже существует"


class AuthServiceError(ProjectException):
    reason = "Ошибка аутентификации"


class UserAlreadyVerified(AuthServiceError):
    reason = "Email адрес пользователя уже подтверждён"


class UserNotVerified(AuthServiceError):
    reason = "Номер телефона пользователя не подтверждён"


class InvalidPassword(AuthServiceError):
    reason = "Невалидный пароль"


class PasswordMatch(ErrorFieldsMixin, AuthServiceError):
    reason = "Новый пароль не может совпадать с текущим паролем"


class PasswordMismatch(ErrorFieldsMixin, AuthServiceError):
    reason = "Неверный старый пароль"


class InvalidTokenError(AuthServiceError):
    reason = "Невалидный токен"
