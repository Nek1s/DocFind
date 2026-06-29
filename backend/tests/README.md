# Тесты бэкенда DocFind

## Запуск
Из каталога `backend/` в окружении с dev-зависимостями:

```bash
pip install -r requirements-dev.txt   # pytest, pytest-cov, Pillow и пр.
pytest -q                             # весь набор тестов
```

## Покрытие (QA-01, цель ≥50%)

```bash
pytest --cov=. --cov-report=term-missing
```

Конфигурация — в `backend/.coveragerc`: меряется код приложения, а сами тесты и
генератор фикстур из охвата исключены. Текущее покрытие кода приложения — ~98%.

## Состав
- `test_documents.py`, `test_upload_endpoint.py` — эндпоинт загрузки (BE-01).
- `test_document_service.py`, `test_validation_edges.py` — валидация (BE-02/03).
- `test_text_extraction.py` — извлечение и чанкирование текста (BE-04/05).
- `test_elasticsearch.py` — клиент и индекс Elasticsearch (BE-06/07).
- `test_app.py` — каркас приложения и единый конверт ошибок.
- `test_fixtures.py` — целостность набора тестовых документов (QA-03).
- `fixtures/` — набор тестовых документов (см. `fixtures/README.md`).
- `conftest.py`, `_util.py` — общие фикстуры и построители тестовых файлов.
