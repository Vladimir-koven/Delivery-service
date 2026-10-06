from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_settings_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
)


class AppSettings(BaseSettings):
    """Настройки приложения."""

    model_config = _settings_config

    name: str = Field(default="delivery-service", alias="APP_NAME")
    env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=True, alias="APP_DEBUG")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")  # nosec B104
    port: int = Field(default=8000, alias="APP_PORT")


class DatabaseSettings(BaseSettings):
    """Настройки подключения к PostgreSQL."""

    model_config = _settings_config

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


class JwtSettings(BaseSettings):
    """Настройки JWT-авторизации."""

    model_config = _settings_config

    secret: str = Field(alias="JWT_SECRET")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")


class Settings(BaseSettings):
    """Корневой объект настроек."""

    model_config = _settings_config

    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    jwt: JwtSettings = JwtSettings()


@lru_cache
def get_settings() -> Settings:
    """Вернуть singleton-настройки (кэшируется)."""
    return Settings()


settings = get_settings()
