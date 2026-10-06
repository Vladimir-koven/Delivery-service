"""Доменные исключения.

Публичный API: импортируtv отсюда, не из подмодулей.
"""

from delivery.exceptions.auth import (
    AuthenticationError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from delivery.exceptions.base import ConflictError, DomainError, NotFoundError
from delivery.exceptions.courier import CourierNotFoundError
from delivery.exceptions.order import (
    OrderNotFoundError,
    OrderStatusTransitionError,
)

__all__ = [
    "AuthenticationError",
    "ConflictError",
    "CourierNotFoundError",
    "DomainError",
    "EmailAlreadyExistsError",
    "InactiveUserError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "NotFoundError",
    "OrderNotFoundError",
    "OrderStatusTransitionError",
]
