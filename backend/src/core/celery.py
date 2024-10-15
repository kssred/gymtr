from logging.config import dictConfig

from celery.app import Celery
from celery.signals import setup_logging

from src.core.config import settings
from src.logs.config import LOG_CONFIG
from src.utils.enums import BytesTo, SecondsTo

REDIS_URL = f"{settings.REDIS.URL}/1"

celery_app = Celery(
    __name__,
    broker=REDIS_URL,
    backend=REDIS_URL,
    broker_connection_retry_on_startup=False,
)

celery_app.autodiscover_tasks(
    [
        "src.services.auth",
        "src.services.mail",
        "src.logs",
    ]
)

celery_app.conf.beat_schedule = {
    "write-logs": {
        "task": "log-write-file",
        "schedule": (
            settings.LOG.CHECK_TIMEOUT if not settings.DEBUG else SecondsTo.ONE_MINUTE
        ),
        "kwargs": {
            "writer_path": settings.LOG.WRITER_PATH,
            "writer_kwargs": {"file_size": BytesTo.ONE_MB * 10},
        },
    }
}


@setup_logging.connect
def setup_loggers(*args, **kwargs):
    dictConfig(LOG_CONFIG)
