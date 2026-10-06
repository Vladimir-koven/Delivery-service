from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from delivery.depends import CourierServiceDep, CurrentUserDep
from delivery.schemas.courier import (
    CourierCreate,
    CourierRead,
    CourierStatus,
    CourierUpdate,
)

router = APIRouter(prefix="/couriers", tags=["couriers"])


@router.post(
    "",
    response_model=CourierRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать курьера",
)
async def create_courier(
    data: CourierCreate,
    service: CourierServiceDep,
    _: CurrentUserDep,
) -> CourierRead:
    """Создать нового курьера (требует авторизации)."""
    return await service.create(data)


@router.get(
    "",
    response_model=list[CourierRead],
    summary="Список курьеров",
)
async def list_couriers(
    service: CourierServiceDep,
    courier_status: Annotated[
        CourierStatus | None,
        Query(alias="status"),
    ] = None,
) -> list[CourierRead]:
    """Список курьеров с опциональным фильтром по статусу (публичный)."""
    return await service.list(status=courier_status)


@router.get(
    "/{courier_id}",
    response_model=CourierRead,
    summary="Получить курьера",
)
async def get_courier(
    courier_id: UUID,
    service: CourierServiceDep,
) -> CourierRead:
    """Получить курьера по id (публичный)."""
    return await service.get(courier_id)


@router.patch(
    "/{courier_id}",
    response_model=CourierRead,
    summary="Обновить курьера",
)
async def update_courier(
    courier_id: UUID,
    data: CourierUpdate,
    service: CourierServiceDep,
    _: CurrentUserDep,
) -> CourierRead:
    """Частично обновить курьера (требует авторизации)."""
    return await service.update(courier_id, data)


@router.delete(
    "/{courier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить курьера",
)
async def delete_courier(
    courier_id: UUID,
    service: CourierServiceDep,
    _: CurrentUserDep,
) -> None:
    """Удалить курьера (требует авторизации)."""
    await service.delete(courier_id)
