from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Настройки приложения."""

    name: str = Field(default="delivery-service", alias="APP_NAME")
    env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=True, alias="APP_DEBUG")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")  # nosec B104
    port: int = Field(default=8000, alias="APP_PORT")


class DatabaseSettings(BaseSettings):
    """Настройки подключения к PostgreSQL."""

    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="delivery", alias="POSTGRES_USER")
    password: str = Field(default="change_me_in_prod", alias="POSTGRES_PASSWORD")
    name: str = Field(default="delivery", alias="POSTGRES_DB")

    @property
    def url(self) -> str:
        """DSN для SQLAlchemy (async)."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )


class Settings(BaseSettings):
    """Корневой объект настроек."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()


@lru_cache
def get_settings() -> Settings:
    """Вернуть singleton-настройки (кэшируется)."""
    return Settings()


settings = get_settings()
