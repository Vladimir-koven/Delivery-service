"""create orders table

Revision ID: 93d8482ce4e4
Revises: 87bbf4aa6d12
Create Date: 2026-10-05 22:20:51.605689

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "93d8482ce4e4"
down_revision: str | Sequence[str] | None = "87bbf4aa6d12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ORDER_STATUS_VALUES = ("created", "assigned", "in_progress", "delivered", "cancelled")


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаём ENUM-тип order_status
    order_status = postgresql.ENUM(*ORDER_STATUS_VALUES, name="order_status")
    order_status.create(op.get_bind(), checkfirst=True)

    # 2. Создаём таблицу orders
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("courier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("customer_name", sa.String(length=100), nullable=False),
        sa.Column("customer_phone", sa.String(length=20), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                *ORDER_STATUS_VALUES,
                name="order_status",
                create_type=False,
            ),
            server_default="created",
            nullable=False,
        ),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["courier_id"],
            ["couriers.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_orders_courier_id"),
        "orders",
        ["courier_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_orders_courier_id"), table_name="orders")
    op.drop_table("orders")
    sa.Enum(name="order_status").drop(op.get_bind(), checkfirst=True)
