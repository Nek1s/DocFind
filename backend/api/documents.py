"""Маршруты загрузки документов (BE-01)."""
from fastapi import APIRouter, HTTPException, UploadFile

from core.config import settings
from models.schemas import UploadResponse
from services.document_service import make_document_id, validate_document

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, summary="Загрузка документа")
async def upload_document(file: UploadFile) -> UploadResponse:
    """Принять PDF/DOCX, провалидировать и вернуть сгенерированный UUID."""
    # Ранний отказ по объявленному размеру, чтобы не читать огромный payload в память.
    if file.size is not None and file.size > settings.max_upload_size:
        limit_mb = settings.max_upload_size // (1024 * 1024)
        raise HTTPException(400, f"Файл превышает максимальный размер {limit_mb} МБ.")

    content = await file.read()
    content_type = validate_document(file.filename, content)
    return UploadResponse(
        id=make_document_id(),
        filename=file.filename,
        size=len(content),
        content_type=content_type,
    )
