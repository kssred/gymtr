from fastapi import status

from src.api.v1.error import AuthErrorCode, UserErrorCode
from src.schemas.error import ErrorSchema
from src.typing import OpenAPIResponseType

ME_GET_RESPONSES: OpenAPIResponseType = {
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
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    AuthErrorCode.USER_NOT_VERIFIED: {
                        "summary": "Пользователь не подтверждён",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.USER_NOT_VERIFIED,
                                "reason": "Пользователь не подтверждён",
                            }
                        },
                    },
                }
            }
        },
    },
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
}

ME_PATCH_RESPONSES: OpenAPIResponseType = {
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
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorSchema,
        "content": {
            "application/json": {
                "examples": {
                    AuthErrorCode.USER_NOT_VERIFIED: {
                        "summary": "Пользователь не подтверждён",
                        "value": {
                            "detail": {
                                "code": AuthErrorCode.USER_NOT_VERIFIED,
                                "reason": "Пользователь не подтверждён",
                            }
                        },
                    },
                }
            }
        },
    },
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
