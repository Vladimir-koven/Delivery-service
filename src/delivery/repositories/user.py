from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.models.user import User
from delivery.schemas.user import UserCreate, UserRole


class UserRepository:
    """Репозиторий для работы с пользователями в БД."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Найти пользователя по id."""
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        data: UserCreate,
        hashed_password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Создать нового пользователя."""
        user = User(
            email=str(data.email),
            hashed_password=hashed_password,
            full_name=data.full_name,
            role=role,
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def list(
        self,
        role: UserRole | None = None,
    ) -> list[User]:
        """Список пользователей, опционально с фильтром по роли."""
        stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
        if role is not None:
            stmt = stmt.where(User.role == role)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, user: User, data: dict) -> User:
        """Частично обновить пользователя."""
        for field, value in data.items():
            setattr(user, field, value)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Удалить пользователя."""
        await self._session.delete(user)
        await self._session.commit()
