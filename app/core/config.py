# app/core/config.py

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(...)
    OWNER_ID: int = Field(0)

    DATABASE_URL: str = Field("sqlite+aiosqlite:///mrbot.db")

    LOG_LEVEL: str = "INFO"

    JWT_SECRET: str = Field("CHANGE_ME")
    SENTRY_DSN: str = Field("")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()