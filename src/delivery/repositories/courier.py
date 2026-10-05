from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.models.courier import Courier
from delivery.schemas.courier import CourierCreate, CourierStatus, CourierUpdate


class CourierRepository:
    """Репозиторий для работы с курьерами в БД."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, courier_id: UUID) -> Courier | None:
        """Найти курьера по id. Возвращает None, если не найден."""
        stmt = select(Courier).order_by(Courier.created_at.desc(), Courier.id.desc())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        status: CourierStatus | None = None,
    ) -> list[Courier]:
        """Список курьеров, опционально с фильтром по статусу."""
        stmt = select(Courier).order_by(Courier.created_at.desc(), Courier.id.desc())
        if status is not None:
            stmt = stmt.where(Courier.status == status)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: CourierCreate) -> Courier:
        """Создать нового курьера."""
        courier = Courier(
            full_name=data.full_name,
            phone=data.phone,
            status=data.status,
        )
        self._session.add(courier)
        await self._session.commit()
        await self._session.refresh(courier)
        return courier

    async def update(self, courier: Courier, data: CourierUpdate) -> Courier:
        """Обновить существующего курьера."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(courier, field, value)
        await self._session.commit()
        await self._session.refresh(courier)
        return courier

    async def delete(self, courier: Courier) -> None:
        """Удалить курьера."""
        await self._session.delete(courier)
        await self._session.commit()
