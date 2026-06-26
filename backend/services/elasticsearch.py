"""Интеграция с Elasticsearch (BE-06).

Спринт 1 — подключение: единый асинхронный клиент и проверка доступности.
Создание индекса и маппинг добавятся в Спринте 2.

Клиент создаётся лениво и хранится модульным синглтоном, чтобы переиспользовать
пул соединений между запросами. URL читается из настроек приложения (.env).
"""
from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from core.config import settings

# Единственный экземпляр клиента на процесс. None — ещё не создан / уже закрыт.
_client: AsyncElasticsearch | None = None


def get_es_client() -> AsyncElasticsearch:
    """Вернуть общий асинхронный клиент Elasticsearch (ленивая инициализация)."""
    global _client
    if _client is None:
        _client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
    return _client


async def close_es_client() -> None:
    """Закрыть клиент и сбросить синглтон. Вызывается при остановке приложения."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None


async def ping() -> bool:
    """Проверить доступность Elasticsearch.

    Сетевые/прочие ошибки не пробрасываем (возвращаем False): старт приложения
    не должен падать из-за временно недоступного ES.
    """
    try:
        return await get_es_client().ping()
    except Exception:
        return False
