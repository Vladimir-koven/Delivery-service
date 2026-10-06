from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from delivery.config import settings
from delivery.core.logging import setup_logging
from delivery.core.middleware import RequestLoggingMiddleware
from delivery.exceptions.handlers import register_exception_handlers
from delivery.routing import api_router

setup_logging()


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=settings.app.name,
        version="0.1.0",
        debug=settings.app.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging — последним (выполняется первым)
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router)

    logger.info(
        "app_created",
        app=settings.app.name,
        env=settings.app.env,
        debug=settings.app.debug,
    )

    return app


app = create_app()
