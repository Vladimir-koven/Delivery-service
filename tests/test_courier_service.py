from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from delivery.models.courier import Courier
from delivery.schemas.courier import CourierCreate, CourierStatus, CourierUpdate
from delivery.services.courier import CourierNotFoundError, CourierService


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repository: AsyncMock) -> CourierService:
    return CourierService(mock_repository)


def _make_courier(
    full_name: str = "Ivan",
    phone: str = "+79991112233",
    status: CourierStatus = CourierStatus.OFFLINE,
) -> Courier:
    """Создать ORM-объект Courier (без сохранения в БД)."""
    courier = Courier(full_name=full_name, phone=phone, status=status)
    # id и timestamps обычно заполняются при commit, для теста зададим явно
    courier.id = uuid4()
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    courier.created_at = now
    courier.updated_at = now
    return courier


async def test_get_returns_courier(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    courier = _make_courier()
    mock_repository.get_by_id.return_value = courier

    result = await service.get(courier.id)

    assert result.id == courier.id
    assert result.full_name == "Ivan"
    mock_repository.get_by_id.assert_awaited_once_with(courier.id)


async def test_get_raises_not_found(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CourierNotFoundError):
        await service.get(uuid4())


async def test_create_returns_read(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    courier = _make_courier()
    mock_repository.create.return_value = courier
    data = CourierCreate(full_name="Ivan", phone="+79991112233")

    result = await service.create(data)

    assert result.id == courier.id
    mock_repository.create.assert_awaited_once_with(data)


async def test_list_returns_reads(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    couriers = [_make_courier(full_name="Ivan"), _make_courier(full_name="Petr")]
    mock_repository.list.return_value = couriers

    result = await service.list()

    assert len(result) == 2
    assert result[0].full_name == "Ivan"
    assert result[1].full_name == "Petr"


async def test_update_raises_not_found(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CourierNotFoundError):
        await service.update(uuid4(), CourierUpdate(status=CourierStatus.BUSY))


async def test_delete_raises_not_found(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CourierNotFoundError):
        await service.delete(uuid4())


async def test_delete_calls_repository(
    service: CourierService, mock_repository: AsyncMock
) -> None:
    courier = _make_courier()
    mock_repository.get_by_id.return_value = courier

    await service.delete(courier.id)

    mock_repository.delete.assert_awaited_once_with(courier)