from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.config import Settings, get_settings
from delivery.db.session import async_session_maker
from delivery.exceptions import InvalidTokenError
from delivery.repositories.courier import CourierRepository
from delivery.repositories.order import OrderRepository
from delivery.repositories.user import UserRepository
from delivery.schemas.user import UserRead
from delivery.services.auth import AuthService
from delivery.services.courier import CourierService
from delivery.services.order import OrderService

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# База данных
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД. Автоматически закрывается после запроса."""
    async with async_session_maker() as session:
        yield session


# Courier
def get_courier_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CourierRepository:
    """Repository курьеров, привязанный к сессии."""
    return CourierRepository(session)


def get_courier_service(
    repository: Annotated[CourierRepository, Depends(get_courier_repository)],
) -> CourierService:
    """Сервис курьеров."""
    return CourierService(repository)


# Order
def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrderRepository:
    """Repository заказов, привязанный к сессии."""
    return OrderRepository(session)


def get_order_service(
    repository: Annotated[OrderRepository, Depends(get_order_repository)],
    courier_repository: Annotated[CourierRepository, Depends(get_courier_repository)],
) -> OrderService:
    """Сервис заказов."""
    return OrderService(repository, courier_repository)


# User / Auth
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """Repository пользователей, привязанный к сессии."""
    return UserRepository(session)


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    """Сервис аутентификации."""
    return AuthService(repository)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    """Получить текущего пользователя из JWT.

    Здесь HTTPException уместен: нужен специфичный заголовок WWW-Authenticate.
    """
    try:
        return await service.get_user_by_token(token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Алиасы
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
CourierServiceDep = Annotated[CourierService, Depends(get_courier_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[UserRead, Depends(get_current_user)]
