/** Публичная точка входа сервисного слоя: API-клиент и доменные методы. */
export { apiRequest, ApiError, API_BASE_URL } from './apiClient'
export { uploadDocument } from './documents'
export { getHealth } from './system'
export type { UploadResponse, HealthResponse, ApiErrorBody } from './types'
