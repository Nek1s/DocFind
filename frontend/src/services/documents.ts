import { apiRequest } from './apiClient'
import type { UploadResponse } from './types'

/**
 * Загрузить документ на сервер: POST /documents/upload (multipart/form-data).
 *
 * Поле формы — «file»: оно должно совпадать с именем параметра FastAPI-эндпоинта
 * (`upload_document(file: UploadFile)`). Content-Type вручную не задаём — браузер
 * сам проставит `multipart/form-data` с корректным boundary.
 */
export function uploadDocument(file: File, signal?: AbortSignal): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  return apiRequest<UploadResponse>('/documents/upload', {
    method: 'POST',
    body: form,
    signal,
  })
}
