"""create users table

Revision ID: 7153bceadd51
Revises: 93d8482ce4e4
Create Date: 2026-10-06 19:18:40.422178

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7153bceadd51"
down_revision: str | Sequence[str] | None = "93d8482ce4e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_ROLE_VALUES = ("admin", "user", "courier")


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаём ENUM-тип user_role
    user_role = postgresql.ENUM(*USER_ROLE_VALUES, name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)

    # 2. Создаём таблицу users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                *USER_ROLE_VALUES,
                name="user_role",
                create_type=False,
            ),
            server_default="user",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
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
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
