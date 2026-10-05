from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(StrEnum):
    """Статус заказа."""

    CREATED = "created"  # создан, курьер не назначен
    ASSIGNED = "assigned"  # курьер назначен
    IN_PROGRESS = "in_progress"  # в пути к клиенту
    DELIVERED = "delivered"  # доставлен
    CANCELLED = "cancelled"  # отменён


class OrderBase(BaseModel):
    """Общие поля заказа."""

    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: str = Field(min_length=5, max_length=20)
    address: str = Field(min_length=5, max_length=500)
    total_amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class OrderCreate(OrderBase):
    """Схема для создания заказа.
    Заказ всегда создаётся в статусе CREATED без курьера.
    Курьер назначается отдельным эндпоинтом.
    """


class OrderUpdate(BaseModel):
    """Схема для частичного обновления заказа."""

    customer_name: str | None = Field(default=None, min_length=2, max_length=100)
    customer_phone: str | None = Field(default=None, min_length=5, max_length=20)
    address: str | None = Field(default=None, min_length=5, max_length=500)
    total_amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class OrderRead(OrderBase):
    """Схема для чтения заказа (то, что отдаём наружу)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    courier_id: UUID | None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
