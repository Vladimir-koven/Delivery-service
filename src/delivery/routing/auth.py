from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from delivery.depends import AuthServiceDep, CurrentUserDep
from delivery.schemas.user import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация",
)
async def register(
    data: UserCreate,
    service: AuthServiceDep,
) -> UserRead:
    """Зарегистрировать нового пользователя."""
    return await service.register(data)


@router.post(
    "/login",
    response_model=Token,
    summary="Логин",
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> Token:
    """Логин по email и паролю. Возвращает JWT."""
    user = await service.authenticate(form.username, form.password)
    token = await service.create_token(user)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Текущий пользователь",
)
async def me(current_user: CurrentUserDep) -> UserRead:
    """Получить текущего пользователя по JWT."""
    return current_user
