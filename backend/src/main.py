from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.core.config import settings
from src.events import check_db_connection
from src.logs.config import LOG_CONFIG
from src.middlewares import LoggingMiddleware
from src.offline import set_offline

if settings.ENV_STATE != "TEST":
    dictConfig(LOG_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection()

    yield


app = FastAPI(
    root_path="/api/v1",
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    swagger_ui_parameters=settings.SWAGGER.model_dump(),
    docs_url=None,
    lifespan=lifespan,
)
set_offline(app)

app.include_router(api_router)


app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers="*",
)
