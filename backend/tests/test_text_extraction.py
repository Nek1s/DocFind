"""Тесты сервиса извлечения и чанкирования текста (BE-04, BE-05).

Спринт 1 — чанкирование (BE-05): генератор `chunk_text`.
"""
import pytest

from services.text_extraction import chunk_text


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
