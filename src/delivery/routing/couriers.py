from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from delivery.depends import CourierServiceDep
from delivery.schemas.courier import (
    CourierCreate,
    CourierRead,
    CourierStatus,
    CourierUpdate,
)
from delivery.services.courier import CourierNotFoundError

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
) -> CourierRead:
    """Создать нового курьера."""
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
    """Список курьеров с опциональным фильтром по статусу."""
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
    """Получить курьера по id."""
    try:
        return await service.get(courier_id)
    except CourierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.patch(
    "/{courier_id}",
    response_model=CourierRead,
    summary="Обновить курьера",
)
async def update_courier(
    courier_id: UUID,
    data: CourierUpdate,
    service: CourierServiceDep,
) -> CourierRead:
    """Частично обновить курьера."""
    try:
        return await service.update(courier_id, data)
    except CourierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/{courier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить курьера",
)
async def delete_courier(
    courier_id: UUID,
    service: CourierServiceDep,
) -> None:
    """Удалить курьера."""
    try:
        await service.delete(courier_id)
    except CourierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
