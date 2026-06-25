"""Pydantic-схемы запросов/ответов API."""
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Ответ на успешную загрузку документа."""

    id: UUID
    filename: str
    size: int
    content_type: str
