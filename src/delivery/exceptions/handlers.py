from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from delivery.exceptions.base import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    """Зарегистрировать обработчики доменных исключений."""

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        """Единый обработчик всех доменных ошибок."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )
