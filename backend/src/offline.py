from typing import Optional

from fastapi import FastAPI as FastAPIOriginal
from fastapi import Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.core.config.base import BASE_DIR

STATIC_DIR = BASE_DIR / "staticfiles"


def set_offline(
    app: FastAPIOriginal, docs_url: Optional[str] = "/docs"
) -> FastAPIOriginal:
    static_url = "/staticfiles"

    app.mount(
        static_url,
        StaticFiles(directory=STATIC_DIR.as_posix()),
        name="docs-offline",
    )

    if docs_url:

        @app.get(docs_url, include_in_schema=False)
        async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
            root = request.scope.get("root_path")

            return get_swagger_ui_html(
                openapi_url=f"{root}{app.openapi_url}",
                title=app.title + " - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url=f"{root}{static_url}/swagger-ui-bundle.js",
                swagger_css_url=f"{root}{static_url}/swagger-ui.css",
                swagger_ui_parameters=app.swagger_ui_parameters,
            )

        if app.swagger_ui_oauth2_redirect_url:

            @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
            async def swagger_ui_redirect() -> HTMLResponse:
                return get_swagger_ui_oauth2_redirect_html()

    return app
