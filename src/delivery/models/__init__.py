"""Все модели должны быть импортированы здесь, чтобы попасть в Base.metadata.
Это критично для:
- Alembic autogenerate (migrations/env.py)
- Base.metadata.create_all (тесты, dev-окружение)
"""

from delivery.models.courier import Courier

__all__ = ["Courier"]
