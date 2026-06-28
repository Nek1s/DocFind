"""Проверка целостности набора тестовых документов (QA-03).

Тесты гарантируют, что фикстуры на месте и ведут себя так, как заявлено в
каталоге (README): корректные — валидируются и парсятся, негативные —
отбраковываются `validate_document`, битые — роняют извлечение текста.

Набор и маркеры берутся из `generate_fixtures` (единый источник правды), а
поведение проверяется через рабочий код приложения: `validate_document`
(BE-02) и `extract_pages` (BE-04).
"""
import pytest

from services.document_service import DocumentValidationError, validate_document
from services.text_extraction import TextExtractionError, extract_pages
from tests.fixtures import generate_fixtures as fx

ALL_DOCS = (
    fx.VALID_DOCS
    + fx.VALID_NO_TEXT
    + fx.COMPLEX_DOCS
    + fx.NEGATIVE_DOCS
    + fx.CORRUPT_DOCS
)


def _read(rel_path: str) -> bytes:
    return (fx.FIXTURES_DIR / rel_path).read_bytes()


@pytest.mark.parametrize("rel_path", ALL_DOCS)
def test_fixture_file_exists(rel_path):
    assert (fx.FIXTURES_DIR / rel_path).is_file(), f"нет фикстуры: {rel_path}"


# --- Корректные документы: проходят валидацию и парсятся ---------------------


@pytest.mark.parametrize("rel_path", fx.VALID_DOCS)
def test_valid_doc_passes_validation_and_extracts_text(rel_path):
    content = _read(rel_path)
    validate_document(rel_path, content)  # не бросает
    pages = extract_pages(rel_path, content)
    assert pages, "ожидалась хотя бы одна страница"
    assert any(p.text.strip() for p in pages), "ожидался непустой текстовый слой"


def test_simple_docx_contains_marker():
    pages = extract_pages("valid/simple.docx", _read("valid/simple.docx"))
    assert fx.SIMPLE_TEXT in pages[0].text


def test_large_docx_has_substantial_text():
    pages = extract_pages("valid/large.docx", _read("valid/large.docx"))
    assert fx.LARGE_MARKER in pages[0].text
    assert len(pages[0].text) > 100_000  # действительно «большой» документ


@pytest.mark.parametrize("rel_path", fx.VALID_NO_TEXT)
def test_scanned_pdf_valid_but_has_no_text_layer(rel_path):
    content = _read(rel_path)
    assert validate_document(rel_path, content) == "application/pdf"
    pages = extract_pages(rel_path, content)
    assert pages, "у скана должны быть страницы"
    assert all(p.text == "" for p in pages), "у скана нет извлекаемого текста"


# --- Сложные, но валидные документы -----------------------------------------


@pytest.mark.parametrize("rel_path", fx.COMPLEX_DOCS)
def test_complex_doc_validates_and_extracts_without_error(rel_path):
    content = _read(rel_path)
    validate_document(rel_path, content)
    assert extract_pages(rel_path, content), "ожидалась хотя бы одна страница"


def test_table_heading_extracted_but_cells_are_not():
    # Текущий парсер читает только document.paragraphs, поэтому текст ячеек
    # таблицы теряется. Заголовок (абзац) извлекается, содержимое таблицы — нет.
    # Это задокументированное ограничение (см. README, кандидат в баг-репорт #38).
    text = extract_pages("complex/with_table.docx", _read("complex/with_table.docx"))[0].text
    assert fx.TABLE_HEADING in text
    assert fx.TABLE_ROW[0] not in text


def test_image_docx_caption_extracted():
    text = extract_pages("complex/with_image.docx", _read("complex/with_image.docx"))[0].text
    assert fx.IMAGE_CAPTION in text


def test_nonstandard_font_text_extracted():
    text = extract_pages(
        "complex/nonstandard_font.docx", _read("complex/nonstandard_font.docx")
    )[0].text
    assert fx.FONT_TEXT in text


# --- Негативные кейсы: отбраковываются валидацией ----------------------------


@pytest.mark.parametrize("rel_path", fx.NEGATIVE_DOCS)
def test_negative_doc_rejected_by_validation(rel_path):
    with pytest.raises(DocumentValidationError):
        validate_document(rel_path, _read(rel_path))


def test_oversized_pdf_rejected_by_validation(oversized_pdf_bytes):
    with pytest.raises(DocumentValidationError):
        validate_document("oversized.pdf", oversized_pdf_bytes)


# --- Битые документы: ломают извлечение текста -------------------------------


def test_truncated_pdf_passes_magic_but_fails_extraction():
    content = _read("corrupt/truncated.pdf")
    # Сигнатуры %PDF достаточно для поверхностной валидации...
    assert validate_document("corrupt/truncated.pdf", content) == "application/pdf"
    # ...но реальное извлечение текста на битой структуре падает.
    with pytest.raises(TextExtractionError):
        extract_pages("corrupt/truncated.pdf", content)


def test_corrupt_docx_rejected_and_fails_extraction():
    content = _read("corrupt/not_a_zip.docx")
    with pytest.raises(DocumentValidationError):
        validate_document("corrupt/not_a_zip.docx", content)
    with pytest.raises(TextExtractionError):
        extract_pages("corrupt/not_a_zip.docx", content)
