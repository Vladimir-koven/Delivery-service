"""Все модели должны быть импортированы здесь, чтобы попасть в Base.metadata.
Это критично для:
- Alembic autogenerate (migrations/env.py)
- Base.metadata.create_all (тесты, dev-окружение)
"""

from delivery.models.courier import Courier
from delivery.models.order import Order
from delivery.models.user import User, UserRole

__all__ = ["Courier", "Order", "User", "UserRole"]
