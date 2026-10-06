from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(StrEnum):
    """Роль пользователя."""

    ADMIN = "admin"
    USER = "user"
    COURIER = "courier"


class UserBase(BaseModel):
    """Общие поля пользователя."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)


class UserCreate(UserBase):
    """Схема для регистрации пользователя."""

    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    """Схема для чтения пользователя (то, что отдаём наружу)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """Схема для логина."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Ответ с JWT-токеном."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Полезная нагрузка JWT-токена."""

    sub: str  # user id
    exp: int  # expiration timestamp
