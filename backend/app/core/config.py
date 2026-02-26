# app/core/config.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – pydantic-settings
#
# pydantic-settings reads configuration from:
#   1. Environment variables (highest priority)
#   2. A .env file
#   3. The default values defined in the class
#
# This means the same code works in Docker (env vars injected by Compose)
# and locally (values from .env file).
#
# Why a Settings class instead of os.getenv() calls everywhere?
#   - All config in one place
#   - Type validation (e.g., PORT must be an int)
#   - Easy to test by constructing Settings(port=9999) in tests
# ─────────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App metadata
    app_name: str = "MyTeams API"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Server
    backend_port: int = 8000
    log_level: str = "info"

    # Database (not used until CP6)
    database_url: str = "sqlite:///./myteams.db"

    model_config = SettingsConfigDict(
        # Look for a .env file in the current working directory
        env_file=".env",
        # Ignore extra env vars that don't map to fields
        extra="ignore",
    )


# Single shared instance – import this across the app
settings = Settings()
