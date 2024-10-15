from src.core.config import settings

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "src.logs.formatter.JSONLogFormatter",
            "pii_patterns": [
                "password",
            ],
            "exclude_patterns": [
                "file",
            ],
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "storage": {
            "formatter": "json",
            "class": "src.logs.handlers.StorageHandler",
        },
    },
    "loggers": {
        "src": {
            "handlers": ["console", "storage"],
            "level": settings.LOG.LEVEL,
            "propagate": False,
        },
        "src.logs.tasks": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "src.logs.writer": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "storage"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.worker": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
