import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RepairFlow"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://repairflow:repairflow@postgres:5432/repairflow"

    bot_token: str = ""
    manager_ids: str = ""

    google_credentials: str = ""
    google_sheet_id: str = ""

    jwt_secret: str = Field(default="change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def manager_telegram_ids(self) -> list[int]:
        if not self.manager_ids.strip():
            return []
        return [int(item.strip()) for item in self.manager_ids.split(",") if item.strip()]

    @property
    def google_credentials_dict(self) -> dict | None:
        if not self.google_credentials:
            return None
        try:
            return json.loads(self.google_credentials)
        except json.JSONDecodeError:
            return None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
