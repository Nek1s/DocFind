"""Тесты интеграции с Elasticsearch (BE-06, Спринт 1): клиент и ping.

ES в тестах не поднимаем — клиент мокаем, поэтому набор работает офлайн и быстро.
Асинхронные функции вызываем через asyncio.run, чтобы не тянуть pytest-asyncio.
"""
import asyncio
from unittest.mock import patch

from elasticsearch import AsyncElasticsearch, BadRequestError
from elastic_transport import ApiResponseMeta, HttpHeaders

import services.elasticsearch as es
from core.config import settings


def _bad_request(message: str) -> BadRequestError:
    """Собрать настоящий BadRequestError с заданным типом ошибки ES (для тестов гонки)."""
    meta = ApiResponseMeta(
        status=400, http_version="1.1", headers=HttpHeaders({}), duration=0.0, node=None
    )
    return BadRequestError(message, meta=meta, body={})


def teardown_function() -> None:
    """Сбросить синглтон между тестами, чтобы они не влияли друг на друга."""
    asyncio.run(es.close_es_client())


def test_get_es_client_is_singleton():
    """get_es_client отдаёт один и тот же сконфигурированный клиент."""
    first = es.get_es_client()
    second = es.get_es_client()
    assert first is second
    assert isinstance(first, AsyncElasticsearch)


def test_get_es_client_uses_url_from_settings(monkeypatch):
    """Клиент создаётся с хостом из settings.elasticsearch_url.

    Проверяем поведенчески — какой URL передан конструктору AsyncElasticsearch,
    а не внутренности transport.node_pool (это internal API библиотеки).
    """
    monkeypatch.setattr(settings, "elasticsearch_url", "http://es.example:9200")
    asyncio.run(es.close_es_client())  # сбросить, чтобы клиент пересоздался с новым URL
    with patch.object(es, "AsyncElasticsearch") as mock_cls:
        es.get_es_client()
    mock_cls.assert_called_once_with(hosts=["http://es.example:9200"])
    es._client = None  # синглтон держит mock — сбрасываем, чтобы teardown не звал close()


class _FakeClient:
    """Заглушка ES-клиента: фиксирует close и управляет поведением ping."""

    def __init__(self, ping_result=True, ping_error=None):
        self._ping_result = ping_result
        self._ping_error = ping_error
        self.closed = False

    async def ping(self):
        if self._ping_error is not None:
            raise self._ping_error
        return self._ping_result

    async def close(self):
        self.closed = True


def test_ping_returns_true_when_available(monkeypatch):
    monkeypatch.setattr(es, "_client", _FakeClient(ping_result=True))
    assert asyncio.run(es.ping()) is True


def test_ping_returns_false_on_connection_error(monkeypatch):
    """Сетевые ошибки не пробрасываются — старт приложения не должен падать."""
    monkeypatch.setattr(es, "_client", _FakeClient(ping_error=ConnectionError("down")))
    assert asyncio.run(es.ping()) is False


def test_close_es_client_closes_and_resets(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(es, "_client", fake)
    asyncio.run(es.close_es_client())
    assert fake.closed is True
    assert es._client is None


def test_app_starts_even_if_elasticsearch_down(monkeypatch):
    """Приложение поднимается и отвечает на /health, даже если ES недоступен."""
    import main
    from fastapi.testclient import TestClient

    async def _ping_down():
        return False

    monkeypatch.setattr(main, "ping", _ping_down)
    with TestClient(main.create_app()) as client:
        assert client.get("/api/v1/health").status_code == 200


# --- Спринт 2: настройки/маппинг индекса и автосоздание ---------------------


def test_index_settings_define_russian_analyzer():
    """В настройках индекса есть кастомный анализатор 'ru' c русскими фильтрами."""
    analysis = es.INDEX_SETTINGS["analysis"]
    ru = analysis["analyzer"]["ru"]
    assert ru["filter"] == ["lowercase", "russian_stop", "russian_stemmer"]
    assert analysis["filter"]["russian_stop"]["stopwords"] == "_russian_"
    assert analysis["filter"]["russian_stemmer"]["language"] == "russian"


def test_index_mappings_cover_chunk_fields():
    """Маппинг описывает поля чанка (BE-07) с корректными типами; text — на 'ru'."""
    props = es.INDEX_MAPPINGS["properties"]
    assert props["chunk_id"]["type"] == "keyword"
    assert props["file_name"]["type"] == "keyword"
    assert props["page_number"]["type"] == "integer"
    assert props["text"]["type"] == "text"
    assert props["text"]["analyzer"] == "ru"


class _FakeIndices:
    """Заглушка namespace client.indices: фиксирует вызов create, может бросать ошибку."""

    def __init__(self, exists: bool, create_error: Exception | None = None):
        self._exists = exists
        self._create_error = create_error
        self.create_kwargs = None

    async def exists(self, index):
        return self._exists

    async def create(self, *, index, settings, mappings):
        self.create_kwargs = {"index": index, "settings": settings, "mappings": mappings}
        if self._create_error is not None:
            raise self._create_error


class _FakeClientWithIndices:
    def __init__(self, exists: bool, create_error: Exception | None = None):
        self.indices = _FakeIndices(exists, create_error)


def test_ensure_index_skips_when_exists(monkeypatch):
    fake = _FakeClientWithIndices(exists=True)
    monkeypatch.setattr(es, "_client", fake)
    created = asyncio.run(es.ensure_index())
    assert created is False
    assert fake.indices.create_kwargs is None


def test_ensure_index_creates_when_absent(monkeypatch):
    fake = _FakeClientWithIndices(exists=False)
    monkeypatch.setattr(es, "_client", fake)
    created = asyncio.run(es.ensure_index())
    assert created is True
    kwargs = fake.indices.create_kwargs
    assert kwargs["index"] == settings.es_index_name
    assert kwargs["settings"] == es.INDEX_SETTINGS
    assert kwargs["mappings"] == es.INDEX_MAPPINGS


def test_ensure_index_handles_concurrent_create_race(monkeypatch):
    """Гонка: другой воркер уже создал индекс между exists и create.

    ES отвечает resource_already_exists_exception (BadRequestError) — это не ошибка,
    индекс есть. ensure_index должна вернуть False, не пробрасывая исключение.
    """
    race = _bad_request("resource_already_exists_exception")
    fake = _FakeClientWithIndices(exists=False, create_error=race)
    monkeypatch.setattr(es, "_client", fake)
    assert asyncio.run(es.ensure_index()) is False


def test_ensure_index_reraises_other_bad_request(monkeypatch):
    """Прочие BadRequestError (например, некорректные настройки) — пробрасываем."""
    other = _bad_request("illegal_argument_exception")
    fake = _FakeClientWithIndices(exists=False, create_error=other)
    monkeypatch.setattr(es, "_client", fake)
    try:
        asyncio.run(es.ensure_index())
        raised = False
    except BadRequestError:
        raised = True
    assert raised is True


def test_startup_creates_index_when_es_available(monkeypatch):
    """При доступном ES старт приложения вызывает ensure_index()."""
    import main
    from fastapi.testclient import TestClient

    calls = []

    async def _ping_up():
        return True

    async def _ensure():
        calls.append(True)
        return True

    monkeypatch.setattr(main, "ping", _ping_up)
    monkeypatch.setattr(main, "ensure_index", _ensure)
    with TestClient(main.create_app()) as client:
        assert client.get("/api/v1/health").status_code == 200
    assert calls == [True]
