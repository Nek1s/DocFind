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

    # Ограничения загрузки документов (BE-02). Список разрешённых форматов —
    # единый источник в services.document_service._FORMAT_VALIDATORS.
    max_upload_size: int = 20 * 1024 * 1024  # 20 МБ

    # Elasticsearch (BE-06). URL берётся из окружения (в docker-compose уже задан);
    # дефолт — для локального запуска без контейнера.
    elasticsearch_url: str = "http://localhost:9200"
    es_index_name: str = "documents"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
