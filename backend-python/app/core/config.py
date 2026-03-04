"""Application configuration via pydantic-settings and .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load and validate settings from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "fastapi-backend"
    env: str = "development"
    debug: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"

    jwt_issuer: str = "fastapi-backend"
    jwt_audience: str = "fastapi-backend"
    jwt_secret: str = "change_me_to_a_long_random_value"
    jwt_access_expires_minutes: int = 15
    jwt_refresh_expires_days: int = 7

    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton Settings (fail fast on first access if validation fails)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
