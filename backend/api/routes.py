"""Маршруты API версии v1."""
from fastapi import APIRouter

from api.documents import router as documents_router
from core.config import settings

api_router = APIRouter()
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])


@api_router.get("/health", tags=["system"], summary="Проверка работоспособности")
async def health() -> dict:
    """Вернуть статус сервиса и его версию (liveness-проба)."""
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}
