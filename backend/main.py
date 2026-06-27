"""Точка входа бэкенда DocFind.

Собирает FastAPI-приложение: подключает маршруты API и регистрирует
глобальные обработчики HTTP-ошибок. Запуск для разработки:

    uvicorn main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import api_router
from core.config import settings
from core.exceptions import register_exception_handlers
from services.elasticsearch import close_es_client, ensure_index, ping

logger = logging.getLogger("docfind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: проверка ES при старте, закрытие при остановке.

    Если ES доступен — создаём индекс `documents` (если его нет). Если недоступен
    или создание не удалось — логируем и продолжаем работу (без падения старта).
    """
    if await ping():
        logger.info("Подключение к Elasticsearch установлено (%s).", settings.elasticsearch_url)
        try:
            created = await ensure_index()
            logger.info(
                "Индекс '%s' %s.",
                settings.es_index_name,
                "создан" if created else "уже существует",
            )
        except Exception:
            logger.exception("Не удалось создать индекс '%s'.", settings.es_index_name)
    else:
        logger.warning(
            "Elasticsearch недоступен на старте (%s). Приложение продолжит работу.",
            settings.elasticsearch_url,
        )
    yield
    await close_es_client()


def create_app() -> FastAPI:
    """Создать и сконфигурировать экземпляр приложения FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
