from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from delivery.depends import CurrentUserDep, OrderServiceDep
from delivery.schemas.order import (
    OrderAssignCourier,
    OrderCreate,
    OrderRead,
    OrderStatus,
    OrderStatusUpdate,
    OrderUpdate,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ",
)
async def create_order(
    data: OrderCreate,
    service: OrderServiceDep,
    _: CurrentUserDep,
) -> OrderRead:
    """Создать новый заказ (требует авторизации)."""
    return await service.create(data)


@router.get(
    "",
    response_model=list[OrderRead],
    summary="Список заказов",
)
async def list_orders(
    service: OrderServiceDep,
    order_status: Annotated[
        OrderStatus | None,
        Query(alias="status"),
    ] = None,
    courier_id: Annotated[
        UUID | None,
        Query(),
    ] = None,
) -> list[OrderRead]:
    """Список заказов с фильтрами (публичный)."""
    return await service.list(status=order_status, courier_id=courier_id)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Получить заказ",
)
async def get_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderRead:
    """Получить заказ по id (публичный)."""
    return await service.get(order_id)


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Обновить заказ",
)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    service: OrderServiceDep,
    _: CurrentUserDep,
) -> OrderRead:
    """Частично обновить заказ (требует авторизации)."""
    return await service.update(order_id, data)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заказ",
)
async def delete_order(
    order_id: UUID,
    service: OrderServiceDep,
    _: CurrentUserDep,
) -> None:
    """Удалить заказ (требует авторизации)."""
    await service.delete(order_id)


@router.post(
    "/{order_id}/assign",
    response_model=OrderRead,
    summary="Назначить курьера на заказ",
)
async def assign_courier(
    order_id: UUID,
    data: OrderAssignCourier,
    service: OrderServiceDep,
    _: CurrentUserDep,
) -> OrderRead:
    """Назначить курьера на заказ (требует авторизации)."""
    return await service.assign_courier(order_id, data.courier_id)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Сменить статус заказа",
)
async def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    service: OrderServiceDep,
    _: CurrentUserDep,
) -> OrderRead:
    """Сменить статус заказа (требует авторизации)."""
    return await service.update_status(order_id, data.status)
