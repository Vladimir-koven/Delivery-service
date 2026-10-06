from delivery.exceptions.base import ConflictError, DomainError


class EmailAlreadyExistsError(ConflictError):
    code = "email_already_exists"


class AuthenticationError(DomainError):
    status_code = 401
    code = "authentication_error"


class InvalidCredentialsError(AuthenticationError):
    code = "invalid_credentials"


class InvalidTokenError(AuthenticationError):
    code = "invalid_token"


class InactiveUserError(DomainError):
    status_code = 403
    code = "inactive_user"
