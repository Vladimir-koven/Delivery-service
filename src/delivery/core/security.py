"""Безопасность: хеширование паролей и работа с JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt
from passlib.context import CryptContext

from delivery.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Захешировать пароль (bcrypt)."""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль против хеша."""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Создать JWT access token для субъекта (обычно user id)."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt.access_token_expire_minutes)

    now = datetime.now(UTC)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": now,
    }
    return cast(
        str,
        jwt.encode(
            payload,
            settings.jwt.secret,
            algorithm=settings.jwt.algorithm,
        ),
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Декодировать JWT. Возвращает payload или None, если токен невалиден."""
    try:
        return cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.jwt.secret,
                algorithms=[settings.jwt.algorithm],
            ),
        )
    except JWTError:
        return None
