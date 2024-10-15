from fastapi import status

from src.api.v1.error import AuthErrorCode, UserErrorCode
from src.schemas.error import ErrorSchema
from src.typing import OpenAPIResponseType

LOGIN_POST_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    AuthErrorCode.BAD_CREDENTIALS: {
                        "summary": "Не верные данные или пользователь не активен",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.BAD_CREDENTIALS,
                                "reason": "Указан неверный логин или пароль",
                                "error_fields": None,
                            }
                        },
                    },
                }
            }
        },
    }
}

REFRESH_GET_RESPONSES: OpenAPIResponseType = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    AuthErrorCode.BAD_TOKEN: {
                        "summary": "Невалидный токен",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.BAD_TOKEN,
                                "reason": "Невалидный или просроченный токен",
                                "error_fields": None,
                            }
                        },
                    }
                }
            }
        },
    }
}

REGISTER_POST_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    AuthErrorCode.INVALID_PASSWORD: {
                        "summary": "Пароль не прошёл валидацию",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.INVALID_PASSWORD,
                                "reason": "Длина пароля должна быть больше 8 символов",
                                "error_fields": ["password"],
                            }
                        },
                    }
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    UserErrorCode.USER_ALREADY_EXIST: {
                        "summary": "Пользователь с такими данными уже зарегистрирован",
                        "value": {
                            "detail": {
                                "code": UserErrorCode.USER_ALREADY_EXIST,
                                "reason": "Пользователь с такими данными уже зарегистрирован",
                                "error_fields": ["email"],
                            }
                        },
                    },
                }
            }
        },
    },
}
