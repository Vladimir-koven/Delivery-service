from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.config import Settings, get_settings
from delivery.db.session import async_session_maker
from delivery.repositories.courier import CourierRepository
from delivery.repositories.order import OrderRepository
from delivery.services.courier import CourierService
from delivery.services.order import OrderService


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


def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrderRepository:
    return OrderRepository(session)


# Service
def get_courier_service(
    repository: Annotated[CourierRepository, Depends(get_courier_repository)],
) -> CourierService:
    """Сервис курьеров."""
    return CourierService(repository)


def get_order_service(
    repository: Annotated[OrderRepository, Depends(get_order_repository)],
    courier_repository: Annotated[CourierRepository, Depends(get_courier_repository)],
) -> OrderService:
    return OrderService(repository, courier_repository)


# Алиасы
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
CourierServiceDep = Annotated[CourierService, Depends(get_courier_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
