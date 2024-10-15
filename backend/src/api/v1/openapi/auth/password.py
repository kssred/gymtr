from fastapi import status

from src.api.v1.error import AuthErrorCode, MailErrorCode, UserErrorCode
from src.schemas.error import ErrorSchema
from src.typing import OpenAPIResponseType

PUT_PASSWORD_CHANGE_RESPONSES: OpenAPIResponseType = {
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
    },
    status.HTTP_409_CONFLICT: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    1: {
                        "summary": "Новые пароли не совпадают",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.INVALID_PASSWORD,
                                "reason": "Новые пароли не совпадают",
                            }
                        },
                    },
                    2: {
                        "summary": "Пароль слишком распространённый",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.INVALID_PASSWORD,
                                "reason": "Пароль слишком распространённый",
                            }
                        },
                    },
                    AuthErrorCode.USER_PASSWORD_MATCH: {
                        "summary": "Новый и старый пароль не могут совпадать",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.USER_PASSWORD_MATCH,
                                "reason": "Новый и старый пароль не могут совпадать",
                            }
                        },
                    },
                    AuthErrorCode.USER_PASSWORD_MISMATCH: {
                        "summary": "Неверный старый пароль",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.USER_PASSWORD_MISMATCH,
                                "reason": "Неверный старый пароль",
                            }
                        },
                    },
                }
            }
        },
    },
}

POST_PASSWORD_RESET_RESPONSES: OpenAPIResponseType = {
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    UserErrorCode.USER_NOT_EXIST: {
                        "summary": "Пользователь не найден",
                        "value": {
                            "detail": {
                                "code": UserErrorCode.USER_NOT_EXIST,
                                "reason": "Пользователь не найден",
                            }
                        },
                    },
                }
            }
        },
    },
    status.HTTP_502_BAD_GATEWAY: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    MailErrorCode.SEND_ERROR: {
                        "summary": "Ошибка сервиса рассылки",
                        "value": {
                            "detail": {
                                "code": MailErrorCode.SEND_ERROR,
                                "reason": "Ошибка при отправке сообщения",
                            }
                        },
                    }
                }
            }
        },
    },
}

PATCH_PASSWORD_RESET_RESPONSES: OpenAPIResponseType = {}
