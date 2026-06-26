"""Интеграция с Elasticsearch (BE-06).

Спринт 1 — подключение: единый асинхронный клиент и проверка доступности.
Спринт 2 — индекс `documents`: русскоязычный анализатор, маппинг, автосоздание.

Клиент создаётся лениво и хранится модульным синглтоном, чтобы переиспользовать
пул соединений между запросами. URL читается из настроек приложения (.env).
"""
from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from core.config import settings

# Единственный экземпляр клиента на процесс. None — ещё не создан / уже закрыт.
_client: AsyncElasticsearch | None = None

# Русскоязычный анализатор для качественного полнотекстового поиска (критерий
# «analysis-ru»). Собран из встроенных компонентов ES — без сторонних плагинов
# (установка плагина = правка Docker-образа, это зона DevOps, не бэкенда):
#   lowercase        — приведение к нижнему регистру;
#   russian_stop     — отбрасывание русских стоп-слов;
#   russian_stemmer  — стемминг (snowball) для совпадения словоформ.
INDEX_SETTINGS = {
    "analysis": {
        "filter": {
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "stemmer", "language": "russian"},
        },
        "analyzer": {
            "ru": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "russian_stop", "russian_stemmer"],
            }
        },
    }
}

# Маппинг под чанк документа (BE-07): метаданные — keyword/integer (точное
# совпадение, фильтрация), сам текст — text с русским анализатором (поиск).
INDEX_MAPPINGS = {
    "properties": {
        "chunk_id": {"type": "keyword"},
        "file_name": {"type": "keyword"},
        "page_number": {"type": "integer"},
        "text": {"type": "text", "analyzer": "ru"},
    }
}


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


async def ensure_index() -> bool:
    """Создать индекс `documents`, если его ещё нет. Идемпотентна.

    Возвращает True, если индекс был создан, False — если уже существовал.
    """
    client = get_es_client()
    if await client.indices.exists(index=settings.es_index_name):
        return False
    await client.indices.create(
        index=settings.es_index_name,
        settings=INDEX_SETTINGS,
        mappings=INDEX_MAPPINGS,
    )
    return True
