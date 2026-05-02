from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NextStep Backend"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "backend/nextstep.db"
    artifacts_dir: Path = Field(default_factory=lambda: Path("backend/artifacts"))
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    processed_data_dir: Path = Field(default_factory=lambda: Path("data/processed"))
    mappings_dir: Path = Field(default_factory=lambda: Path("data/mappings"))
    
    # Auth settings
    secret_key: str = "demo-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_prefix="NEXTSTEP_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
