from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from delivery.depends import OrderServiceDep
from delivery.schemas.order import (
    OrderAssignCourier,
    OrderCreate,
    OrderRead,
    OrderStatus,
    OrderStatusUpdate,
    OrderUpdate,
)
from delivery.services.courier import CourierNotFoundError
from delivery.services.order import (
    OrderNotFoundError,
    OrderStatusTransitionError,
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
) -> OrderRead:
    """Создать новый заказ (статус = created, курьер не назначен)."""
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
    """Список заказов с опциональными фильтрами по статусу и курьеру."""
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
    """Получить заказ по id."""
    try:
        return await service.get(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Обновить заказ",
)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    service: OrderServiceDep,
) -> OrderRead:
    """Частично обновить клиентские поля заказа."""
    try:
        return await service.update(order_id, data)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заказ",
)
async def delete_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> None:
    """Удалить заказ."""
    try:
        await service.delete(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post(
    "/{order_id}/assign",
    response_model=OrderRead,
    summary="Назначить курьера на заказ",
)
async def assign_courier(
    order_id: UUID,
    data: OrderAssignCourier,
    service: OrderServiceDep,
) -> OrderRead:
    """Назначить курьера. Заказ должен быть в статусе created, курьер — available."""
    try:
        return await service.assign_courier(order_id, data.courier_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CourierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except OrderStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Сменить статус заказа",
)
async def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    service: OrderServiceDep,
) -> OrderRead:
    """Сменить статус заказа. Проверяет допустимость перехода."""
    try:
        return await service.update_status(order_id, data.status)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except OrderStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
