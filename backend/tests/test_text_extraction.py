"""Тесты сервиса извлечения и чанкирования текста (BE-04, BE-05).

Спринт 1 — чанкирование (BE-05): генератор `chunk_text`.
Спринт 2 — извлечение (BE-04): `extract_pages` для PDF/DOCX.
"""
import io
from pathlib import Path

import docx
import pytest

from services.text_extraction import (
    PageText,
    TextExtractionError,
    chunk_text,
    extract_pages,
)

SAMPLE_PDF = (Path(__file__).parent / "fixtures" / "sample.pdf").read_bytes()


def _make_docx(*paragraphs: str) -> bytes:
    """Собрать валидный DOCX с заданными абзацами (через сам python-docx)."""
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_short_text_returns_single_chunk():
    assert list(chunk_text("abc", size=10, overlap=3)) == ["abc"]


def test_empty_text_returns_no_chunks():
    assert list(chunk_text("", size=10, overlap=3)) == []


def test_chunks_cover_text_with_overlap():
    # 20 символов, окно 10, перекрытие 3 → шаг 7, старты 0,7,14.
    text = "0123456789ABCDEFGHIJ"
    assert list(chunk_text(text, size=10, overlap=3)) == [
        "0123456789",
        "789ABCDEFG",
        "EFGHIJ",
    ]


def test_each_chunk_overlaps_previous_by_overlap():
    text = "0123456789ABCDEFGHIJ"
    chunks = list(chunk_text(text, size=10, overlap=3))
    for prev, nxt in zip(chunks, chunks[1:]):
        assert nxt[:3] == prev[-3:]  # хвост предыдущего = начало следующего


def test_default_window_is_1000_with_overlap_100():
    text = "x" * 2500
    chunks = list(chunk_text(text))
    assert len(chunks[0]) == 1000
    # второй чанк стартует на 900-м символе (шаг 1000-100)
    assert chunks[1] == text[900:1900]


def test_overlap_not_less_than_size_raises():
    with pytest.raises(ValueError):
        list(chunk_text("abc", size=10, overlap=10))


def test_negative_overlap_raises():
    with pytest.raises(ValueError):
        list(chunk_text("abc", size=10, overlap=-1))


# --- BE-04: извлечение текста ---


def test_extract_pdf_returns_text_per_page():
    pages = extract_pages("lecture.pdf", SAMPLE_PDF)
    assert [p.page_number for p in pages] == [1, 2, 3]
    assert "алгоритмы" in pages[0].text
    assert "структуры данных" in pages[1].text
    assert pages[2].text == ""  # пустая страница без текстового слоя


def test_extract_docx_joins_paragraphs_on_single_page():
    content = _make_docx("Первый абзац", "Второй абзац")
    pages = extract_pages("notes.docx", content)
    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "Первый абзац" in pages[0].text
    assert "Второй абзац" in pages[0].text


def test_extract_returns_pagetext_objects():
    pages = extract_pages("notes.docx", _make_docx("текст"))
    assert isinstance(pages[0], PageText)


def test_unsupported_extension_raises():
    with pytest.raises(ValueError):
        extract_pages("data.txt", b"plain")


def test_corrupt_pdf_raises_extraction_error():
    with pytest.raises(TextExtractionError):
        extract_pages("broken.pdf", b"%PDF-1.4 not really a pdf")


def test_corrupt_docx_raises_extraction_error():
    with pytest.raises(TextExtractionError):
        extract_pages("broken.docx", b"PK\x03\x04 not a docx")
