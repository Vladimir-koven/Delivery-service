from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from delivery.models.courier import Courier
from delivery.models.order import Order
from delivery.schemas.courier import CourierStatus
from delivery.schemas.order import (
    OrderCreate,
    OrderStatus,
    OrderStatusUpdate,
    OrderUpdate,
)
from delivery.services.courier import CourierNotFoundError
from delivery.services.order import (
    OrderNotFoundError,
    OrderService,
    OrderStatusTransitionError,
)


@pytest.fixture
def order_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def courier_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(order_repo: AsyncMock, courier_repo: AsyncMock) -> OrderService:
    return OrderService(order_repo, courier_repo)


def _now() -> datetime:
    return datetime.now(UTC)


def _make_order(
    *,
    status: OrderStatus = OrderStatus.CREATED,
    courier_id=None,
) -> Order:
    order = Order(
        customer_name="Alice",
        customer_phone="+79995556677",
        address="ул. Пушкина, д. 1",
        total_amount=Decimal("1500.50"),
        status=status,
        courier_id=courier_id,
    )
    order.id = uuid4()
    order.created_at = _now()
    order.updated_at = _now()
    return order


def _make_courier(
    *,
    status: CourierStatus = CourierStatus.AVAILABLE,
) -> Courier:
    courier = Courier(
        full_name="Courier",
        phone="+79991112233",
        status=status,
    )
    courier.id = uuid4()
    courier.created_at = _now()
    courier.updated_at = _now()
    return courier


async def test_get_returns_order(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order = _make_order()
    order_repo.get_by_id.return_value = order

    result = await service.get(order.id)

    assert result.id == order.id
    order_repo.get_by_id.assert_awaited_once_with(order.id)


async def test_get_raises_not_found(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await service.get(uuid4())


async def test_create_returns_read(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order = _make_order()
    order_repo.create.return_value = order
    data = OrderCreate(
        customer_name="Alice",
        customer_phone="+79995556677",
        address="ул. Пушкина, д. 1",
        total_amount=Decimal("1500.50"),
    )

    result = await service.create(data)

    assert result.id == order.id
    order_repo.create.assert_awaited_once_with(data)


async def test_list_returns_reads(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.list.return_value = [_make_order(), _make_order()]

    result = await service.list()

    assert len(result) == 2
    order_repo.list.assert_awaited_once_with(status=None, courier_id=None)


async def test_update_raises_not_found(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await service.update(uuid4(), OrderUpdate(customer_name="Bob"))


async def test_assign_courier_order_not_found(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await service.assign_courier(uuid4(), uuid4())


async def test_assign_courier_courier_not_found(
    service: OrderService, order_repo: AsyncMock, courier_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = _make_order()
    courier_repo.get_by_id.return_value = None

    with pytest.raises(CourierNotFoundError):
        await service.assign_courier(uuid4(), uuid4())


async def test_assign_courier_busy_courier(
    service: OrderService, order_repo: AsyncMock, courier_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = _make_order()
    courier_repo.get_by_id.return_value = _make_courier(status=CourierStatus.BUSY)

    with pytest.raises(OrderStatusTransitionError):
        await service.assign_courier(uuid4(), uuid4())


async def test_assign_courier_to_assigned_order(
    service: OrderService, order_repo: AsyncMock, courier_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = _make_order(status=OrderStatus.ASSIGNED)
    courier_repo.get_by_id.return_value = _make_courier()

    with pytest.raises(OrderStatusTransitionError):
        await service.assign_courier(uuid4(), uuid4())


async def test_assign_courier_success(
    service: OrderService, order_repo: AsyncMock, courier_repo: AsyncMock
) -> None:
    order = _make_order()
    courier = _make_courier()
    order_repo.get_by_id.return_value = order
    courier_repo.get_by_id.return_value = courier
    order_repo.assign_courier.return_value = _make_order(
        status=OrderStatus.ASSIGNED, courier_id=courier.id
    )

    result = await service.assign_courier(order.id, courier.id)

    assert result.status == OrderStatus.ASSIGNED
    order_repo.assign_courier.assert_awaited_once()
    courier_repo.update_status.assert_awaited_once()


async def test_update_status_not_found(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await service.update_status(uuid4(), OrderStatus.CANCELLED)


async def test_update_status_invalid_transition(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = _make_order(status=OrderStatus.CREATED)

    with pytest.raises(OrderStatusTransitionError):
        await service.update_status(uuid4(), OrderStatus.DELIVERED)


async def test_update_status_releases_courier_on_delivered(
    service: OrderService, order_repo: AsyncMock, courier_repo: AsyncMock
) -> None:
    order = _make_order(
        status=OrderStatus.IN_PROGRESS, courier_id=uuid4()
    )
    order_repo.get_by_id.return_value = order
    courier_repo.get_by_id.return_value = _make_courier(status=CourierStatus.BUSY)
    order_repo.update_status.return_value = _make_order(
        status=OrderStatus.DELIVERED
    )

    await service.update_status(order.id, OrderStatus.DELIVERED)

    courier_repo.update_status.assert_awaited_once()


async def test_delete_raises_not_found(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await service.delete(uuid4())


async def test_delete_success(
    service: OrderService, order_repo: AsyncMock
) -> None:
    order = _make_order()
    order_repo.get_by_id.return_value = order

    await service.delete(order.id)

    order_repo.delete.assert_awaited_once_with(order)