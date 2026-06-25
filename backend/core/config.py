"""Конфигурация приложения, читаемая из переменных окружения / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Базовые настройки приложения DocFind.

    Значения берутся из переменных окружения (или файла .env).
    На день 1 нужен минимум; интеграционные настройки (Postgres,
    Elasticsearch, Redis) добавятся в следующих задачах.
    """

    app_name: str = "DocFind API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
