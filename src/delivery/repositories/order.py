from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.models.order import Order
from delivery.schemas.order import OrderCreate, OrderStatus, OrderUpdate


class OrderRepository:
    """Репозиторий для работы с заказами в БД."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Найти заказ по id. Возвращает None, если не найден."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        status: OrderStatus | None = None,
        courier_id: UUID | None = None,
    ) -> list[Order]:
        """Список заказов с опциональными фильтрами."""
        stmt = select(Order).order_by(Order.created_at.desc(), Order.id.desc())
        if status is not None:
            stmt = stmt.where(Order.status == status)
        if courier_id is not None:
            stmt = stmt.where(Order.courier_id == courier_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: OrderCreate) -> Order:
        """Создать новый заказ в статусе CREATED без курьера."""
        order = Order(
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            address=data.address,
            total_amount=data.total_amount,
            status=OrderStatus.CREATED,
            courier_id=None,
        )
        self._session.add(order)
        await self._session.commit()
        await self._session.refresh(order)
        return order

    async def update(self, order: Order, data: OrderUpdate) -> Order:
        """Обновить клиентские поля заказа."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        await self._session.commit()
        await self._session.refresh(order)
        return order

    async def assign_courier(self, order: Order, courier_id: UUID) -> Order:
        """Назначить курьера и перевести заказ в ASSIGNED."""
        order.courier_id = courier_id
        order.status = OrderStatus.ASSIGNED
        await self._session.commit()
        await self._session.refresh(order)
        return order

    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        """Обновить статус заказа."""
        order.status = status
        await self._session.commit()
        await self._session.refresh(order)
        return order

    async def delete(self, order: Order) -> None:
        """Удалить заказ."""
        await self._session.delete(order)
        await self._session.commit()
