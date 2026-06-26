"""Маршруты загрузки документов (BE-01)."""
from fastapi import APIRouter, UploadFile

from core.config import settings
from models.schemas import UploadResponse
from services.document_service import make_document_id, validate_document

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, summary="Загрузка документа")
async def upload_document(file: UploadFile) -> UploadResponse:
    """Принять PDF/DOCX, провалидировать и вернуть сгенерированный UUID."""
    # Читаем максимум max+1 байт: надёжно ограничивает память независимо от
    # заголовков клиента (file.size/Content-Length подделываются). Если файл
    # больше лимита — validate_document отвергнет его по размеру.
    content = await file.read(settings.max_upload_size + 1)
    content_type = validate_document(file.filename, content)
    return UploadResponse(
        id=make_document_id(),
        filename=file.filename,
        size=len(content),
        content_type=content_type,
    )
