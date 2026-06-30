import type { ApiErrorBody } from './types'

/**
 * Базовый префикс API. Путь относительный намеренно: в dev его проксирует Vite
 * (`/api` → http://localhost:8000), в prod — nginx (`/api/` → app:8000).
 * Поэтому хост/порт фронту знать не нужно и отдельная env-переменная не вводится.
 */
export const API_BASE_URL = '/api/v1'

/** Ошибка обращения к API: несёт HTTP-код и (опционально) detail от бэка. */
export class ApiError extends Error {
  readonly status: number
  readonly detail?: unknown

  constructor(status: number, message: string, detail?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

interface RequestOptions {
  method?: string
  body?: BodyInit
  signal?: AbortSignal
}

/**
 * Базовый запрос к API: собирает URL, выполняет fetch, разбирает JSON и
 * нормализует ошибки. Ошибки бэка приходят в формате
 * `{"error": {code, message, detail}}` — превращаем их в {@link ApiError}.
 * Сетевые сбои тоже оборачиваем в ApiError (status 0), чтобы у вызывающего
 * был один тип ошибки.
 */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? 'GET',
      body: options.body,
      signal: options.signal,
    })
  } catch (cause) {
    // Намеренную отмену (signal.abort()) пробрасываем как есть — это не сбой сети.
    if (cause instanceof DOMException && cause.name === 'AbortError') throw cause
    throw new ApiError(0, 'Сеть недоступна. Проверьте подключение к серверу.', cause)
  }

  const payload = await parseBody(response)

  if (!response.ok) {
    const body = payload as Partial<ApiErrorBody> | null
    const message = body?.error?.message ?? `Ошибка запроса (${response.status}).`
    throw new ApiError(response.status, message, body?.error?.detail)
  }

  return payload as T
}

/** Безопасный разбор тела: JSON, исходный текст или null для пустого ответа. */
async function parseBody(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}
