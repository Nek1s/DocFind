"""Тесты интеграции с Elasticsearch (BE-06, Спринт 1): клиент и ping.

ES в тестах не поднимаем — клиент мокаем, поэтому набор работает офлайн и быстро.
Асинхронные функции вызываем через asyncio.run, чтобы не тянуть pytest-asyncio.
"""
import asyncio

from elasticsearch import AsyncElasticsearch

import services.elasticsearch as es
from core.config import settings


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
    """Хост клиента берётся из settings.elasticsearch_url."""
    monkeypatch.setattr(settings, "elasticsearch_url", "http://es.example:9200")
    asyncio.run(es.close_es_client())  # сбросить, чтобы клиент пересоздался с новым URL
    client = es.get_es_client()
    hosts = [str(node.base_url) for node in client.transport.node_pool.all()]
    assert any("es.example:9200" in h for h in hosts)


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
