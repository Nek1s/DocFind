"""Общие pytest-фикстуры для доступа к набору тестовых документов (QA-03)."""
from pathlib import Path

import pytest

from core.config import settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Путь к каталогу тестовых документов ``backend/tests/fixtures``."""
    return FIXTURES_DIR


@pytest.fixture
def read_fixture():
    """Фабрика: читает байты фикстуры по пути относительно каталога fixtures."""

    def _read(rel_path: str) -> bytes:
        return (FIXTURES_DIR / rel_path).read_bytes()

    return _read


@pytest.fixture
def oversized_pdf_bytes() -> bytes:
    """PDF на 1 байт больше лимита загрузки (BE-02).

    Файл >20 МБ не коммитим в репозиторий — собираем в памяти по требованию,
    чтобы проверять отбраковку по размеру без раздувания git.
    """
    return b"%PDF-1.4\n" + b"\x00" * (settings.max_upload_size + 1)
