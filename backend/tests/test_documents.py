"""Тесты эндпоинта загрузки документов (BE-01)."""
import uuid

from fastapi.testclient import TestClient

from core.config import settings
from main import create_app

client = TestClient(create_app())
URL = f"{settings.api_v1_prefix}/documents/upload"

PDF = b"%PDF-1.4\n%pdf body"
DOCX = b"PK\x03\x04" + b"\x00" * 20


def _upload(name, content, ctype="application/octet-stream"):
    return client.post(URL, files={"file": (name, content, ctype)})


def test_upload_pdf_returns_uuid():
    resp = _upload("lecture.pdf", PDF)
    assert resp.status_code == 200
    body = resp.json()
    uuid.UUID(body["id"])  # валидный UUID
    assert body["filename"] == "lecture.pdf"
    assert body["size"] == len(PDF)


def test_upload_docx_ok():
    assert _upload("doc.docx", DOCX).status_code == 200


def test_upload_txt_400():
    assert _upload("notes.txt", b"hello").status_code == 400


def test_upload_oversize_400():
    big = b"%PDF-1.4" + b"\x00" * (settings.max_upload_size + 1)
    assert _upload("big.pdf", big).status_code == 400


def test_upload_spoofed_400():
    assert _upload("fake.pdf", b"not a pdf").status_code == 400


def test_upload_missing_file_422():
    assert client.post(URL).status_code == 422
