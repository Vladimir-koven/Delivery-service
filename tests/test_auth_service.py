from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from delivery.core.security import (
    create_access_token,
    hash_password,
)
from delivery.exceptions import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from delivery.models.user import User
from delivery.schemas.user import UserCreate, UserRole
from delivery.services.auth import AuthService


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> AuthService:
    return AuthService(mock_repo)


def _make_user(
    *,
    email: str = "test@example.com",
    password: str = "strong_password",
    is_active: bool = True,
    role: UserRole = UserRole.USER,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name="Test User",
        role=role,
        is_active=is_active,
    )
    user.id = uuid4()
    now = datetime.now(UTC)
    user.created_at = now
    user.updated_at = now
    return user


async def test_register_success(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = None
    new_user = _make_user()
    mock_repo.create.return_value = new_user
    data = UserCreate(
        email="test@example.com",
        full_name="Test User",
        password="strong_password",
    )
    result = await service.register(data)
    assert result.email == "test@example.com"
    assert result.role == UserRole.USER
    mock_repo.get_by_email.assert_awaited_once_with("test@example.com")
    mock_repo.create.assert_awaited_once()


async def test_register_duplicate_email(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = _make_user()
    with pytest.raises(EmailAlreadyExistsError):
        await service.register(
            UserCreate(
                email="test@example.com",
                full_name="Test",
                password="strong_password",
            )
        )


async def test_authenticate_success(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = _make_user()
    result = await service.authenticate("test@example.com", "strong_password")
    assert result.email == "test@example.com"


async def test_authenticate_wrong_password(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = _make_user()
    with pytest.raises(InvalidCredentialsError):
        await service.authenticate("test@example.com", "wrong")


async def test_authenticate_unknown_email(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = None
    with pytest.raises(InvalidCredentialsError):
        await service.authenticate("nobody@example.com", "any")


async def test_authenticate_inactive_user(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = _make_user(is_active=False)
    with pytest.raises(InactiveUserError):
        await service.authenticate("test@example.com", "strong_password")


async def test_create_token(service: AuthService) -> None:
    from delivery.schemas.user import UserRead
    user = _make_user()
    user_read = UserRead.model_validate(user)
    token = await service.create_token(user_read)
    assert isinstance(token, str)
    assert len(token) > 20


async def test_get_user_by_token_success(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    user = _make_user()
    token = create_access_token(subject=str(user.id))
    mock_repo.get_by_id.return_value = user
    result = await service.get_user_by_token(token)
    assert result.id == user.id
    mock_repo.get_by_id.assert_awaited_once_with(user.id)


async def test_get_user_by_token_invalid(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    with pytest.raises(InvalidTokenError):
        await service.get_user_by_token("garbage")


async def test_get_user_by_token_bad_subject(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    token = create_access_token(subject="not-a-uuid")
    with pytest.raises(InvalidTokenError):
        await service.get_user_by_token(token)


async def test_get_user_by_token_user_not_found(
    service: AuthService, mock_repo: AsyncMock
) -> None:
    user_id = uuid4()
    token = create_access_token(subject=str(user_id))
    mock_repo.get_by_id.return_value = None
    with pytest.raises(InvalidTokenError):
        await service.get_user_by_token(token)