from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from delivery.config import settings
from delivery.routing import api_router


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=settings.app.name,
        version="0.1.0",
        debug=settings.app.debug,
    )

    # CORS — для разработки открыто всё, в prod сузим
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем все роутеры
    app.include_router(api_router)

    return app


app = create_app()
