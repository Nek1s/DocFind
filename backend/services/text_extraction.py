"""Извлечение и чанкирование текста документов (BE-04, BE-05).

Спринт 1 — чанкирование (BE-05): генератор `chunk_text`, разбивающий текст на
сегменты фиксированной длины с перекрытием соседних чанков.
Спринт 2 — извлечение (BE-04): `extract_pages` достаёт текст из PDF (pdfplumber)
и DOCX (python-docx) постранично.
Спринт 3 — связка: `iter_chunks` режет текст каждой страницы на чанки и
сохраняет номер страницы — готовый поток для индексации (BE-07).
"""
import io
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import docx
import pdfplumber


class TextExtractionError(Exception):
    """Не удалось извлечь текст: повреждённый/нечитаемый документ."""


@dataclass(frozen=True)
class PageText:
    """Текст одной страницы документа.

    У DOCX нет надёжного понятия «страница» (python-docx не пагинирует), поэтому
    весь его текст возвращается одной страницей с `page_number == 1`.
    """

    page_number: int
    text: str


@dataclass(frozen=True)
class Chunk:
    """Чанк текста с номером страницы-источника — единица индексации (BE-07)."""

    text: str
    page_number: int


def chunk_text(text: str, size: int = 1000, overlap: int = 100) -> Iterator[str]:
    """Разбить текст на чанки по `size` символов с перекрытием `overlap` (BE-05).

    Соседние чанки перекрываются на `overlap` символов — это сохраняет контекст
    на границе сегментов. Шаг между началами чанков равен `size - overlap`.

    Пустой текст не даёт ни одного чанка; текст короче `size` — ровно один.

    :raises ValueError: если `overlap` вне диапазона [0, size).
    """
    if size <= 0:
        raise ValueError("size должен быть положительным.")
    if not 0 <= overlap < size:
        raise ValueError("overlap должен быть в диапазоне [0, size).")

    step = size - overlap
    for start in range(0, len(text), step):
        yield text[start : start + size]
        # Чанк дошёл до конца текста — следующий был бы лишь хвостом-дубликатом.
        if start + size >= len(text):
            break


def extract_pages(filename: str, content: bytes) -> list[PageText]:
    """Извлечь текст документа постранично по расширению файла (BE-04).

    Поддерживаются PDF (pdfplumber) и DOCX (python-docx). На повреждённом или
    нечитаемом файле бросает `TextExtractionError`, на неизвестном расширении —
    `ValueError`.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf(content)
    if ext == ".docx":
        return _extract_docx(content)
    raise ValueError(f"Неподдерживаемый формат для извлечения текста: {ext}")


def _extract_pdf(content: bytes) -> list[PageText]:
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            # extract_text() возвращает None на странице без текстового слоя
            # (например, скан) — нормализуем к пустой строке, а не падаем.
            return [
                PageText(num, page.extract_text() or "")
                for num, page in enumerate(pdf.pages, start=1)
            ]
    except Exception as exc:  # граница парсера: любая ошибка чтения → доменная
        raise TextExtractionError(f"Не удалось прочитать PDF: {exc}") from exc


def _extract_docx(content: bytes) -> list[PageText]:
    try:
        document = docx.Document(io.BytesIO(content))
    except Exception as exc:  # граница парсера: битый zip/не docx → доменная
        raise TextExtractionError(f"Не удалось прочитать DOCX: {exc}") from exc
    text = "\n".join(p.text for p in document.paragraphs)
    return [PageText(1, text)]


def iter_chunks(
    pages: Iterable[PageText], size: int = 1000, overlap: int = 100
) -> Iterator[Chunk]:
    """Превратить страницы в плоский поток чанков с номером страницы (BE-04/05).

    Текст каждой страницы режется `chunk_text` на сегменты `size`/`overlap`,
    каждый чанк наследует `page_number` своей страницы. Пустые страницы не дают
    чанков. Порядок сохраняется: чанки страницы N идут до чанков страницы N+1.

    Глобальный порядковый `chunk_id` присваивает слой индексации (BE-07): ему
    нужен UUID документа, которого здесь нет.
    """
    for page in pages:
        for piece in chunk_text(page.text, size, overlap):
            yield Chunk(piece, page.page_number)
