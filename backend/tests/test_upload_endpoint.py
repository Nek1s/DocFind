"""HTTP-тесты эндпоинта загрузки документов (QA-01, BE-01).

Дополняют `test_documents.py`: проверяют не только статус-код, но и тело ответа
(`content_type`, эхо `filename`/`size`), единый конверт ошибки
(`core/exceptions.py`), границу размера и генерацию UUID. Часть кейсов гоняется
на реальном наборе документов из QA-03 (`tests/fixtures`).

Важно: эндпоинт только валидирует содержимое (сигнатуры), но НЕ извлекает текст,
поэтому `corrupt/truncated.pdf` (сигнатура `%PDF` на месте) загружается успешно —
ошибки парсинга проявляются позже, не на загрузке.
"""
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.documents as documents_api
from core.config import settings
from main import create_app
from tests import _util
from tests.fixtures import generate_fixtures as fx

client = TestClient(create_app())
URL = f"{settings.api_v1_prefix}/documents/upload"

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# Файлы из набора QA-03, которые ПРОХОДЯТ валидацию загрузки.
ACCEPTED = fx.VALID_DOCS + fx.VALID_NO_TEXT + fx.COMPLEX_DOCS + ("corrupt/truncated.pdf",)
# Файлы, которые валидация ОТКЛОНЯЕТ (HTTP 400).
REJECTED = fx.NEGATIVE_DOCS + ("corrupt/not_a_zip.docx",)


def _mime_for(name: str) -> str:
    return PDF_MIME if name.lower().endswith(".pdf") else DOCX_MIME


def _upload(name, content, ctype="application/octet-stream"):
    return client.post(URL, files={"file": (name, content, ctype)})


# --- Успешная загрузка: статус + тело ответа --------------------------------


@pytest.mark.parametrize("rel_path", ACCEPTED)
def test_upload_accepted_returns_200_and_envelope(rel_path):
    name = Path(rel_path).name
    content = (fx.FIXTURES_DIR / rel_path).read_bytes()
    resp = _upload(name, content)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    uuid.UUID(body["id"])  # валидный UUID
    assert body["filename"] == name
    assert body["size"] == len(content)
    assert body["content_type"] == _mime_for(name)


def test_upload_pdf_content_type():
    body = _upload("lecture.pdf", _util.PDF_BYTES).json()
    assert body["content_type"] == PDF_MIME


def test_upload_docx_content_type():
    body = _upload("notes.docx", _util.make_docx_bytes()).json()
    assert body["content_type"] == DOCX_MIME


# --- Негативные кейсы: конверт ошибки ---------------------------------------


@pytest.mark.parametrize("rel_path", REJECTED)
def test_upload_rejected_returns_400_envelope(rel_path):
    name = Path(rel_path).name
    content = (fx.FIXTURES_DIR / rel_path).read_bytes()
    resp = _upload(name, content)
    assert resp.status_code == 400, resp.text
    err = resp.json()["error"]
    assert err["code"] == 400
    assert err["message"]  # непустое описание ошибки


def test_upload_missing_file_returns_422_envelope():
    resp = client.post(URL)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == 422


# --- Граница размера (BE-02) -------------------------------------------------


def test_upload_at_size_limit_ok(max_size_pdf_bytes):
    resp = _upload("limit.pdf", max_size_pdf_bytes)
    assert resp.status_code == 200, resp.text
    assert resp.json()["size"] == settings.max_upload_size


def test_upload_over_limit_returns_400(oversized_pdf_bytes):
    resp = _upload("oversized.pdf", oversized_pdf_bytes)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == 400


# --- Генерация UUID (BE-03) -------------------------------------------------


def test_two_uploads_get_unique_ids():
    first = _upload("a.pdf", _util.PDF_BYTES).json()["id"]
    second = _upload("b.pdf", _util.PDF_BYTES).json()["id"]
    assert first != second


def test_endpoint_returns_generated_uuid(monkeypatch):
    # Изолируем генератор UUID: эндпоинт должен вернуть именно его результат.
    fixed = uuid.UUID("12345678-1234-5678-1234-567812345678")
    monkeypatch.setattr(documents_api, "make_document_id", lambda: fixed)
    body = _upload("x.pdf", _util.PDF_BYTES).json()
    assert body["id"] == str(fixed)
