"""Тесты каркаса приложения: health-эндпоинт и глобальные обработчики ошибок."""
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import create_app


def _client(raise_server_exceptions: bool = True) -> TestClient:
    app = create_app()

    # Временные маршруты для проверки обработчиков 400 и 500.
    @app.get("/_boom_400")
    async def _boom_400():
        raise HTTPException(status_code=400, detail="Некорректный запрос")

    @app.get("/_boom_500")
    async def _boom_500():
        raise RuntimeError("упс")

    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def test_health_ok():
    resp = _client().get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_404_envelope():
    resp = _client().get("/api/v1/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == 404


def test_400_envelope():
    resp = _client().get("/_boom_400")
    assert resp.status_code == 400
    err = resp.json()["error"]
    assert err["code"] == 400
    assert err["message"] == "Некорректный запрос"


def test_500_envelope():
    resp = _client(raise_server_exceptions=False).get("/_boom_500")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == 500


def test_cors_preflight_allows_frontend_origin():
    """Preflight с разрешённого origin получает заголовок Access-Control-Allow-Origin."""
    resp = _client().options(
        "/api/v1/documents/upload",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_blocks_unknown_origin():
    """Запрос с чужого origin не получает CORS-заголовок (список реально ограничивает)."""
    resp = _client().get("/api/v1/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in resp.headers
