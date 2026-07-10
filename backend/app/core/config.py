"""
Centralized application settings.

All configuration is read once here from environment variables / .env file.
No other module should call os.getenv() directly — always import `settings`
from this file. This keeps config changes (e.g. adding a new provider key)
isolated to a single place.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "AI Personal Knowledge Manager"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Auth (used from Step 2 onward) ---
    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- OpenAI (used from Step 6/8 onward) ---
    OPENAI_API_KEY: str = ""

    # --- Gemini ---
    GEMINI_API_KEY: str = ""

    # --- Storage (used from Step 4 onward) ---
    STORAGE_DIR: str = "./storage"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Using lru_cache means the .env file and
    environment are only parsed once per process, and every part of the
    app shares the same Settings instance.
    """
    return Settings()


settings = get_settings()
