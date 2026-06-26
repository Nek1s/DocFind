"""Бизнес-логика загрузки документов: валидация и идентификаторы (BE-02, BE-03).

Сервисный слой не зависит от web-фреймворка: при некорректном документе бросает
доменную ошибку `DocumentValidationError`, которую HTTP-слой конвертирует в ответ 400.
"""
from pathlib import Path
from uuid import UUID, uuid4

from core.config import settings


class DocumentValidationError(ValueError):
    """Документ не прошёл валидацию (формат/размер/содержимое)."""


# Сигнатуры (magic bytes) разрешённых форматов. Content-Type подделывается
# клиентом, поэтому формат проверяем по содержимому, а не только по расширению.
_MAGIC_BYTES = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",  # DOCX — это zip-архив
}

# Канонический MIME-тип по расширению — отдаём его в ответе вместо клиентского.
_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_document(filename: str | None, content: bytes) -> str:
    """Провалидировать документ и вернуть канонический content_type.

    Проверки: имя файла, расширение (PDF/DOCX), непустота, размер ≤ лимита, magic bytes.
    При нарушении бросает `DocumentValidationError`.
    """
    if not filename:
        raise DocumentValidationError("Имя файла не указано.")

    ext = Path(filename).suffix.lower()
    if ext not in _MAGIC_BYTES:
        raise DocumentValidationError(
            f"Недопустимый формат '{ext or filename}'. Разрешены только PDF и DOCX."
        )

    if not content:
        raise DocumentValidationError("Файл пустой.")

    if len(content) > settings.max_upload_size:
        limit_mb = settings.max_upload_size // (1024 * 1024)
        raise DocumentValidationError(f"Файл превышает максимальный размер {limit_mb} МБ.")

    if not content.startswith(_MAGIC_BYTES[ext]):
        raise DocumentValidationError(f"Содержимое файла не соответствует формату {ext}.")

    return _CONTENT_TYPES[ext]


def make_document_id() -> UUID:
    """Сгенерировать уникальный идентификатор документа (BE-03)."""
    return uuid4()
