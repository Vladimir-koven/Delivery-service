from uuid import UUID

from delivery.repositories.courier import CourierRepository
from delivery.schemas.courier import (
    CourierCreate,
    CourierRead,
    CourierStatus,
    CourierUpdate,
)


class CourierNotFoundError(Exception):
    """урьер не найден."""


class CourierService:
    """изнес-логика работы с курьерами."""

    def __init__(self, repository: CourierRepository) -> None:
        self._repository = repository

    async def create(self, data: CourierCreate) -> CourierRead:
        """Создать курьера."""
        courier = await self._repository.create(data)
        return CourierRead.model_validate(courier)

    async def get(self, courier_id: UUID) -> CourierRead:
        """олучить курьера по id. росает CourierNotFoundError."""
        courier = await self._repository.get_by_id(courier_id)
        if courier is None:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        return CourierRead.model_validate(courier)

    async def list(
        self,
        status: CourierStatus | None = None,
    ) -> list[CourierRead]:
        """Список курьеров с опциональным фильтром по статусу."""
        couriers = await self._repository.list(status=status)
        return [CourierRead.model_validate(c) for c in couriers]

    async def update(
        self,
        courier_id: UUID,
        data: CourierUpdate,
    ) -> CourierRead:
        """бновить курьера. росает CourierNotFoundError."""
        courier = await self._repository.get_by_id(courier_id)
        if courier is None:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        updated = await self._repository.update(courier, data)
        return CourierRead.model_validate(updated)

    async def delete(self, courier_id: UUID) -> None:
        """далить курьера. росает CourierNotFoundError."""
        courier = await self._repository.get_by_id(courier_id)
        if courier is None:
            raise CourierNotFoundError(f"Courier {courier_id} not found")
        await self._repository.delete(courier)
