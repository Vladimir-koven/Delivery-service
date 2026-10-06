from uuid import UUID

from delivery.exceptions import (
    CourierNotFoundError,
    OrderNotFoundError,
    OrderStatusTransitionError,
)
from delivery.repositories.courier import CourierRepository
from delivery.repositories.order import OrderRepository
from delivery.schemas.courier import CourierStatus
from delivery.schemas.order import (
    OrderCreate,
    OrderRead,
    OrderStatus,
    OrderUpdate,
)

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.CREATED: {OrderStatus.ASSIGNED, OrderStatus.CANCELLED},
    OrderStatus.ASSIGNED: {OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.IN_PROGRESS: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderService:
    """Бизнес-логика работы с заказами."""

    def __init__(
        self,
        repository: OrderRepository,
        courier_repository: CourierRepository,
    ) -> None:
        self._repository = repository
        self._courier_repository = courier_repository

    async def create(self, data: OrderCreate) -> OrderRead:
        """Создать заказ."""
        order = await self._repository.create(data)
        return OrderRead.model_validate(order)

    async def get(self, order_id: UUID) -> OrderRead:
        """Получить заказ по id. Бросает OrderNotFoundError."""
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return OrderRead.model_validate(order)

    async def list(
        self,
        status: OrderStatus | None = None,
        courier_id: UUID | None = None,
    ) -> list[OrderRead]:
        """Список заказов с фильтрами."""
        orders = await self._repository.list(status=status, courier_id=courier_id)
        return [OrderRead.model_validate(o) for o in orders]

    async def update(self, order_id: UUID, data: OrderUpdate) -> OrderRead:
        """Обновить клиентские поля заказа. Бросает OrderNotFoundError."""
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        updated = await self._repository.update(order, data)
        return OrderRead.model_validate(updated)

    async def assign_courier(self, order_id: UUID, courier_id: UUID) -> OrderRead:
        """Назначить курьера на заказ.

        - Заказ должен существовать.
        - Курьер должен существовать и быть AVAILABLE.
        - Допустимый переход: CREATED -> ASSIGNED.
        """
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")

        courier = await self._courier_repository.get_by_id(courier_id)
        if courier is None:
            raise CourierNotFoundError(f"Courier {courier_id} not found")

        if OrderStatus.ASSIGNED not in ALLOWED_TRANSITIONS[order.status]:
            raise OrderStatusTransitionError(
                f"Cannot assign courier to order in status {order.status}"
            )

        if courier.status != CourierStatus.AVAILABLE:
            raise OrderStatusTransitionError(
                f"Courier {courier_id} is not available (status={courier.status})"
            )

        updated = await self._repository.assign_courier(order, courier_id)
        await self._courier_repository.update_status(courier, CourierStatus.BUSY)
        return OrderRead.model_validate(updated)

    async def update_status(self, order_id: UUID, new_status: OrderStatus) -> OrderRead:
        """Сменить статус заказа.

        - Проверяет допустимость перехода.
        - При DELIVERED / CANCELLED освобождает курьера.
        """
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")

        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise OrderStatusTransitionError(
                f"Cannot transition from {order.status} to {new_status}"
            )

        if (
            new_status in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}
            and order.courier_id is not None
        ):
            courier = await self._courier_repository.get_by_id(order.courier_id)
            if courier is not None:
                await self._courier_repository.update_status(courier, CourierStatus.AVAILABLE)

        updated = await self._repository.update_status(order, new_status)
        return OrderRead.model_validate(updated)

    async def delete(self, order_id: UUID) -> None:
        """Удалить заказ. Бросает OrderNotFoundError."""
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        await self._repository.delete(order)
