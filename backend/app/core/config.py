from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="FitWise AI")
    environment: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./fitwise.db")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")
    storage_dir: str = Field(default="storage")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
