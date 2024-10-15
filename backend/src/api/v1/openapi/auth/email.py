from fastapi import status

from src.api.v1.error import AuthErrorCode, MailErrorCode, UserErrorCode
from src.schemas.error import ErrorSchema
from src.typing import OpenAPIResponseType

GET_EMAIL_CHANGE: OpenAPIResponseType = {
    status.HTTP_409_CONFLICT: {
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
                            }
                        },
                    },
                    UserErrorCode.USER_ALREADY_EXIST: {
                        "summary": "Такой пользователь уже существует",
                        "value": {
                            "detail": {
                                "code": UserErrorCode.USER_ALREADY_EXIST,
                                "reason": "Такой пользователь уже существует",
                            }
                        },
                    },
                }
            }
        },
    },
}

POST_EMAIL_CHANGE: OpenAPIResponseType = {
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
                    UserErrorCode.USER_ALREADY_EXIST: {
                        "summary": "Такой пользователь уже существует",
                        "value": {
                            "detail": {
                                "code": UserErrorCode.USER_ALREADY_EXIST,
                                "reason": "Такой пользователь уже существует",
                            }
                        },
                    },
                }
            }
        },
    },
}

POST_EMAIL_VERIFY_RESPONSES: OpenAPIResponseType = {
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
                    AuthErrorCode.USER_ALREADY_VERIFIED: {
                        "summary": "Пользователь уже подтверждён",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.USER_ALREADY_VERIFIED,
                                "reason": "Email адрес пользователя уже подтверждён",
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

GET_EMAIL_VERIFY_RESPONSES: OpenAPIResponseType = {
    status.HTTP_409_CONFLICT: {
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
                            }
                        },
                    },
                }
            }
        },
    }
}
