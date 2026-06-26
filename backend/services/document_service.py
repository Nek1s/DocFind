"""Бизнес-логика загрузки документов: валидация и идентификаторы (BE-02, BE-03).

Сервисный слой не зависит от web-фреймворка: при некорректном документе бросает
доменную ошибку `DocumentValidationError`, которую HTTP-слой конвертирует в ответ 400.
"""
import io
import zipfile
from pathlib import Path
from uuid import UUID, uuid4

from core.config import settings


class DocumentValidationError(ValueError):
    """Документ не прошёл валидацию (формат/размер/содержимое)."""


def _is_pdf(content: bytes) -> bool:
    """PDF начинается с сигнатуры %PDF."""
    return content.startswith(b"%PDF")


def _is_docx(content: bytes) -> bool:
    """DOCX — это zip-архив, обязательно содержащий word/document.xml.

    Проверка только zip-сигнатуры (PK) недостаточна: под неё подпадают .xlsx,
    .pptx и любой .zip. Поэтому заглядываем внутрь архива.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            return "word/document.xml" in archive.namelist()
    except zipfile.BadZipFile:
        return False


# Валидаторы содержимого по расширению (не доверяем Content-Type от клиента).
# Ключи задают список разрешённых форматов.
_FORMAT_VALIDATORS = {
    ".pdf": _is_pdf,
    ".docx": _is_docx,
}

# Канонический MIME-тип по расширению — отдаём его в ответе вместо клиентского.
_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_document(filename: str | None, content: bytes) -> str:
    """Провалидировать документ и вернуть канонический content_type.

    Проверки: имя файла, расширение (PDF/DOCX), непустота, размер ≤ лимита, содержимое.
    При нарушении бросает `DocumentValidationError`.
    """
    if not filename:
        raise DocumentValidationError("Имя файла не указано.")

    ext = Path(filename).suffix.lower()
    if ext not in _FORMAT_VALIDATORS:
        raise DocumentValidationError(
            f"Недопустимый формат '{ext or filename}'. Разрешены только PDF и DOCX."
        )

    if not content:
        raise DocumentValidationError("Файл пустой.")

    if len(content) > settings.max_upload_size:
        limit_mb = settings.max_upload_size // (1024 * 1024)
        raise DocumentValidationError(f"Файл превышает максимальный размер {limit_mb} МБ.")

    if not _FORMAT_VALIDATORS[ext](content):
        raise DocumentValidationError(f"Содержимое файла не соответствует формату {ext}.")

    return _CONTENT_TYPES[ext]


def make_document_id() -> UUID:
    """Сгенерировать уникальный идентификатор документа (BE-03)."""
    return uuid4()
