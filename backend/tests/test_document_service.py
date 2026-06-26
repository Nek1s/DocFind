"""Юнит-тесты логики валидации документов (BE-02, BE-03)."""
import uuid

import pytest

from core.config import settings
from services.document_service import (
    DocumentValidationError,
    make_document_id,
    validate_document,
)
from tests._util import PDF_BYTES, make_docx_bytes, make_zip_without_word

DOCX_BYTES = make_docx_bytes()


def test_valid_pdf_returns_pdf_content_type():
    assert validate_document("lecture.pdf", PDF_BYTES) == "application/pdf"


def test_valid_docx_returns_docx_content_type():
    assert (
        validate_document("lecture.docx", DOCX_BYTES)
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_uppercase_extension_ok():
    assert validate_document("LECTURE.PDF", PDF_BYTES) == "application/pdf"


def test_disallowed_extension_rejected():
    with pytest.raises(DocumentValidationError):
        validate_document("notes.txt", b"hello")


def test_oversize_rejected():
    big = b"%PDF-1.4" + b"\x00" * (settings.max_upload_size + 1)
    with pytest.raises(DocumentValidationError):
        validate_document("big.pdf", big)


def test_empty_file_rejected():
    with pytest.raises(DocumentValidationError):
        validate_document("empty.pdf", b"")


def test_spoofed_magic_bytes_rejected():
    # расширение .pdf, но содержимое не PDF
    with pytest.raises(DocumentValidationError):
        validate_document("fake.pdf", b"this is not a pdf")


def test_docx_not_a_zip_rejected():
    with pytest.raises(DocumentValidationError):
        validate_document("fake.docx", b"not a zip")


def test_docx_zip_without_word_rejected():
    # валидный zip (напр. .xlsx), но без word/document.xml — не DOCX
    with pytest.raises(DocumentValidationError):
        validate_document("fake.docx", make_zip_without_word())


def test_empty_filename_rejected():
    with pytest.raises(DocumentValidationError):
        validate_document("", PDF_BYTES)


def test_none_filename_rejected():
    with pytest.raises(DocumentValidationError):
        validate_document(None, PDF_BYTES)


def test_make_document_id_is_uuid():
    val = make_document_id()
    assert isinstance(val, uuid.UUID)
    assert make_document_id() != val  # уникальность
