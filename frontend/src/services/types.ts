/**
 * DTO бэкенда DocFind. Имена полей повторяют Pydantic-схемы (models/schemas.py)
 * и единый формат ошибок (core/exceptions.py) — менять только синхронно с бэком.
 */

/** Ответ на успешную загрузку документа: POST /documents/upload. */
export interface UploadResponse {
  id: string
  filename: string
  size: number
  content_type: string
}

/** Ответ health-эндпоинта: GET /health. */
export interface HealthResponse {
  status: string
  service: string
  version: string
}

/**
 * Единый формат ошибки бэка:
 * `{"error": {"code": <int>, "message": <str>, "detail": <any|null>}}`.
 */
export interface ApiErrorBody {
  error: {
    code: number
    message: string
    detail?: unknown
  }
}
