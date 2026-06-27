"""Извлечение и чанкирование текста документов (BE-04, BE-05).

Спринт 1 — чанкирование (BE-05): генератор `chunk_text`, разбивающий текст на
сегменты фиксированной длины с перекрытием соседних чанков.
"""
from collections.abc import Iterator


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
