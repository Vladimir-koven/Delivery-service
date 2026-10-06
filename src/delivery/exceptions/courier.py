from delivery.exceptions.base import NotFoundError


class CourierNotFoundError(NotFoundError):
    """Курьер не найден."""

    code = "courier_not_found"
