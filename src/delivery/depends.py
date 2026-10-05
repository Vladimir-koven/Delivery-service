from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.config import Settings, get_settings
from delivery.db.session import async_session_maker
from delivery.repositories.courier import CourierRepository
from delivery.services.courier import CourierService


# БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД. Автоматически закрывается после запроса."""
    async with async_session_maker() as session:
        yield session


# Repository
def get_courier_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CourierRepository:
    """Repository курьеров, привязанный к сессии."""
    return CourierRepository(session)


# Service
def get_courier_service(
    repository: Annotated[CourierRepository, Depends(get_courier_repository)],
) -> CourierService:
    """Сервис курьеров."""
    return CourierService(repository)


# Алиасы
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
CourierServiceDep = Annotated[CourierService, Depends(get_courier_service)]
