"""Точка входа бэкенда DocFind.

Собирает FastAPI-приложение: подключает маршруты API и регистрирует
глобальные обработчики HTTP-ошибок. Запуск для разработки:

    uvicorn main:app --reload
"""
from fastapi import FastAPI

from api.routes import api_router
from core.config import settings
from core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """Создать и сконфигурировать экземпляр приложения FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
