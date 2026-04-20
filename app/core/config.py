"""app/core/config.py"""

from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	PROJECT_NAME: str = "FASTER_API"
	APP_TITLE: str = "TITLE"
	APP_VERSION: str = "0.0.1"
	APP_DESCRIPTION: str = "DESCRIPTION"

	DATABASE_URL: str = ""
	POSTGRES_DB: str = ""
	POSTGRES_USER: str = ""
	POSTGRES_PASSWORD: str = ""
	POSTGRES_PORT: str = ""

	PASSWORD_PEPPER: str = ""
	SECRET_KEY: str = ""

	REFRESH_TOKEN_COOKIE: str = "refresh_token"
	REFRESH_TOKEN_MAX_AGE: int = 60 * 60 * 24 * 30

	model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
		env_file=".env", extra="allow"
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()


settings = get_settings()
