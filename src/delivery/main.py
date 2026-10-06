from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from delivery.config import settings
from delivery.exceptions.handlers import register_exception_handlers
from delivery.routing import api_router


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=settings.app.name,
        version="0.1.0",
        debug=settings.app.debug,
    )

    # CORS: разрешено всё для локальной разработки.
    # allow_credentials=False, потому что с allow_origins=["*"] браузер
    # не пропускает credentials (правило CORS).
    # В production заменить "*" на явный список доменов frontend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_router)

    return app


app = create_app()
