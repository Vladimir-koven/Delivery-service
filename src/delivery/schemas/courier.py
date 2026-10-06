from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourierStatus(StrEnum):
    """Статус курьера."""

    AVAILABLE = "available"  # свободен, готов взять заказ
    BUSY = "busy"  # на доставке
    OFFLINE = "offline"  # не работает


class CourierBase(BaseModel):
    """Общие поля курьера."""

    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=5, max_length=20)
    status: CourierStatus = CourierStatus.OFFLINE


class CourierCreate(CourierBase):
    """Схема для создания курьера."""


class CourierUpdate(BaseModel):
    """Схема для частичного обновления курьера."""

    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    status: CourierStatus | None = None


class CourierRead(CourierBase):
    """Схема для чтения курьера (то, что отдаём наружу)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
