from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NextStep Backend"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "backend/nextstep.db"
    artifacts_dir: Path = Field(default_factory=lambda: Path("artifacts"))

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_prefix="NEXTSTEP_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
