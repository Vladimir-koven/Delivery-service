from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from delivery.db.base import Base
from delivery.schemas.courier import CourierStatus


class Courier(Base):
    """ORM-модель курьера."""

    __tablename__ = "couriers"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[CourierStatus] = mapped_column(
        PG_ENUM(CourierStatus, name="courier_status", create_type=False),
        nullable=False,
        default=CourierStatus.OFFLINE,
        server_default=CourierStatus.OFFLINE.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Courier id={self.id} name={self.full_name!r} status={self.status}>"
