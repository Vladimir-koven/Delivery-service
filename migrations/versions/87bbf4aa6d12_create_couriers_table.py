"""create couriers table

Revision ID: 87bbf4aa6d12
Revises:
Create Date: 2026-10-04 13:43:01.935551

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "87bbf4aa6d12"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COURIER_STATUS_VALUES = ("available", "busy", "offline")


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаём ENUM-тип courier_status
    courier_status = postgresql.ENUM(
        *COURIER_STATUS_VALUES,
        name="courier_status",
    )
    courier_status.create(op.get_bind(), checkfirst=True)

    # 2. Создаём таблицу couriers
    op.create_table(
        "couriers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                *COURIER_STATUS_VALUES,
                name="courier_status",
                create_type=False,
            ),
            server_default="offline",
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("couriers")
    sa.Enum(name="courier_status").drop(op.get_bind(), checkfirst=True)
