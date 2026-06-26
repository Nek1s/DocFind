"""Глобальные обработчики HTTP-ошибок с единым JSON-форматом ответа.

Любая ошибка отдаётся клиенту в виде:

    {"error": {"code": <int>, "message": <str>, "detail": <any|None>}}

Покрываются коды 400/404 (через HTTPException), ошибки валидации (422)
и непойманные исключения (500).
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.document_service import DocumentValidationError


def _error_response(status_code: int, message: str, detail=None) -> JSONResponse:
    """Сформировать JSON-ответ об ошибке в едином формате."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": status_code, "message": message, "detail": detail}},
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Обработчик HTTPException — покрывает 400, 404 и прочие явные ошибки."""
    return _error_response(exc.status_code, str(exc.detail))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации запроса (некорректные данные → 422)."""
    return _error_response(422, "Ошибка валидации запроса", exc.errors())


async def document_validation_handler(
    request: Request, exc: DocumentValidationError
) -> JSONResponse:
    """Доменная ошибка валидации документа → 400 (web-слой не лезет в сервис)."""
    return _error_response(400, str(exc))


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Обработчик непойманных исключений → 500."""
    return _error_response(500, "Внутренняя ошибка сервера")


def register_exception_handlers(app: FastAPI) -> None:
    """Зарегистрировать все глобальные обработчики ошибок в приложении."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DocumentValidationError, document_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
