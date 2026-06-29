"""Краевые случаи валидации документов (QA-01, BE-02/03).

Дополняют `test_document_service.py` граничными и неочевидными случаями:
точная граница размера, имя файла с несколькими точками, регистр расширения,
позиция сигнатуры, версия UUID.
"""
import pytest

from core.config import settings
from services.document_service import (
    DocumentValidationError,
    make_document_id,
    validate_document,
)
from tests._util import PDF_BYTES, make_docx_bytes

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_content_exactly_at_limit_ok():
    # Проверка размера строгая (`>` лимита), поэтому ровно лимит — проходит.
    header = b"%PDF-1.4\n"
    content = header + b"\x00" * (settings.max_upload_size - len(header))
    assert validate_document("limit.pdf", content) == "application/pdf"


def test_multiple_dots_filename_uses_last_suffix():
    assert validate_document("report.final.v2.pdf", PDF_BYTES) == "application/pdf"


def test_uppercase_docx_extension_ok():
    assert validate_document("NOTES.DOCX", make_docx_bytes()) == DOCX_MIME


def test_pdf_signature_must_be_at_start():
    # `%PDF` не в начале (ведущий пробел) — содержимое не считается PDF.
    with pytest.raises(DocumentValidationError):
        validate_document("x.pdf", b" %PDF-1.4 fake")


def test_make_document_id_is_uuid4():
    assert make_document_id().version == 4
