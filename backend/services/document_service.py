"""Бизнес-логика загрузки документов: валидация и идентификаторы (BE-02, BE-03)."""
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException

from core.config import settings

# Сигнатуры (magic bytes) разрешённых форматов. Content-Type подделывается
# клиентом, поэтому формат проверяем по содержимому, а не только по расширению.
_MAGIC_BYTES = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",  # DOCX — это zip-архив
}


def validate_document(filename: str, content: bytes) -> None:
    """Проверить загружаемый документ. Бросает HTTPException(400) при нарушении.

    Проверки: расширение (PDF/DOCX), непустота, размер ≤ лимита, magic bytes.
    """
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат '{ext or filename}'. Разрешены только PDF и DOCX.",
        )

    if not content:
        raise HTTPException(status_code=400, detail="Файл пустой.")

    if len(content) > settings.max_upload_size:
        limit_mb = settings.max_upload_size // (1024 * 1024)
        raise HTTPException(
            status_code=400, detail=f"Файл превышает максимальный размер {limit_mb} МБ."
        )

    if not content.startswith(_MAGIC_BYTES[ext]):
        raise HTTPException(
            status_code=400,
            detail=f"Содержимое файла не соответствует формату {ext}.",
        )


def make_document_id() -> UUID:
    """Сгенерировать уникальный идентификатор документа (BE-03)."""
    return uuid4()
