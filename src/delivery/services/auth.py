from uuid import UUID

from delivery.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from delivery.exceptions import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from delivery.repositories.user import UserRepository
from delivery.schemas.user import UserCreate, UserRead


class AuthService:
    """Бизнес-логика аутентификации и регистрации."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def register(self, data: UserCreate) -> UserRead:
        """Зарегистрировать пользователя.

        - Проверяет, что email не занят.
        - Хеширует пароль.
        - Создаёт пользователя с ролью USER.
        """
        existing = await self._repository.get_by_email(str(data.email))
        if existing is not None:
            raise EmailAlreadyExistsError(f"Email {data.email} already registered")

        hashed = hash_password(data.password)
        user = await self._repository.create(data, hashed_password=hashed)
        return UserRead.model_validate(user)

    async def authenticate(self, email: str, password: str) -> UserRead:
        """Проверить email и пароль.

        - Если email не найден или пароль неверный — InvalidCredentialsError.
        - Если пользователь деактивирован — InactiveUserError.
        """
        user = await self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InactiveUserError(f"User {email} is inactive")

        return UserRead.model_validate(user)

    async def create_token(self, user: UserRead) -> str:
        """Создать JWT для пользователя."""
        return create_access_token(subject=str(user.id))

    async def get_user_by_token(self, token: str) -> UserRead:
        """Получить пользователя по JWT.

        - Декодирует токен.
        - Если токен невалиден — InvalidTokenError.
        - Если пользователь не найден — InvalidTokenError.
        """
        payload = decode_access_token(token)
        if payload is None or "sub" not in payload:
            raise InvalidTokenError("Invalid token")

        try:
            user_id = UUID(payload["sub"])
        except (ValueError, TypeError) as e:
            raise InvalidTokenError("Invalid token subject") from e

        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise InvalidTokenError("User not found")

        return UserRead.model_validate(user)
