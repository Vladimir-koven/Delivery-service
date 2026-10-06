from typing import Annotated

from fastapi import APIRouter, Depends

from delivery.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    """Проверка работоспособности сервиса."""
    return {
        "status": "ok",
        "service": settings.app.name,
        "env": settings.app.env,
    }
