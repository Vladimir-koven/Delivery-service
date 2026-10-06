from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from delivery import models  # noqa: F401
from delivery.config import settings
from delivery.db.base import Base
from delivery.depends import get_db
from delivery.main import app
from delivery.schemas.courier import CourierStatus
from delivery.schemas.order import OrderStatus


@pytest.fixture
async def engine() -> AsyncGenerator:
    """Движок для тестовой БД (NullPool — не кэширует соединения)."""
    test_engine = create_async_engine(
        settings.db.url,
        poolclass=NullPool,
        echo=False,
    )
    yield test_engine
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def setup_database(engine) -> AsyncGenerator[None, None]:
    """Создать схему и ENUM-типы перед тестом, удалить после."""
    courier_status = PG_ENUM(
        *[e.value for e in CourierStatus],
        name="courier_status",
    )
    order_status = PG_ENUM(
        *[e.value for e in OrderStatus],
        name="order_status",
    )

    async with engine.begin() as conn:
        await conn.run_sync(courier_status.create, checkfirst=True)
        await conn.run_sync(order_status.create, checkfirst=True)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(courier_status.drop, checkfirst=True)
        await conn.run_sync(order_status.drop, checkfirst=True)


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Сессия с транзакцией и откатом после теста."""
    connection = await engine.connect()
    transaction = await connection.begin()

    session_maker = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    async with session_maker() as session:
        yield session

    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент с подменённой зависимостью get_db."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()