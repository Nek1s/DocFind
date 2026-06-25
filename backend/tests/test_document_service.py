"""Юнит-тесты логики валидации документов (BE-02, BE-03)."""
import uuid

import pytest
from fastapi import HTTPException

from core.config import settings
from services.document_service import make_document_id, validate_document

PDF_BYTES = b"%PDF-1.4\n%real pdf content"
DOCX_BYTES = b"PK\x03\x04" + b"\x00" * 20  # zip-сигнатура DOCX


def test_valid_pdf_passes():
    validate_document("lecture.pdf", PDF_BYTES)  # не должно бросить


def test_valid_docx_passes():
    validate_document("lecture.docx", DOCX_BYTES)


def test_uppercase_extension_ok():
    validate_document("LECTURE.PDF", PDF_BYTES)


def test_disallowed_extension_400():
    with pytest.raises(HTTPException) as e:
        validate_document("notes.txt", b"hello")
    assert e.value.status_code == 400


def test_oversize_400():
    big = b"%PDF-1.4" + b"\x00" * (settings.max_upload_size + 1)
    with pytest.raises(HTTPException) as e:
        validate_document("big.pdf", big)
    assert e.value.status_code == 400


def test_empty_file_400():
    with pytest.raises(HTTPException) as e:
        validate_document("empty.pdf", b"")
    assert e.value.status_code == 400


def test_spoofed_magic_bytes_400():
    # расширение .pdf, но содержимое не PDF
    with pytest.raises(HTTPException) as e:
        validate_document("fake.pdf", b"this is not a pdf")
    assert e.value.status_code == 400


def test_docx_wrong_magic_400():
    with pytest.raises(HTTPException) as e:
        validate_document("fake.docx", b"not a zip")
    assert e.value.status_code == 400


def test_make_document_id_is_uuid():
    val = make_document_id()
    assert isinstance(val, uuid.UUID)
    assert make_document_id() != val  # уникальность
