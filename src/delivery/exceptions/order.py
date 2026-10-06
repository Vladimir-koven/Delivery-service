from delivery.exceptions.base import ConflictError, NotFoundError


class OrderNotFoundError(NotFoundError):
    """Заказ не найден."""

    code = "order_not_found"


class OrderStatusTransitionError(ConflictError):
    """Недопустимый переход статуса заказа."""

    code = "order_status_transition_error"
