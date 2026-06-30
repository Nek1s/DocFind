import { apiRequest } from './apiClient'
import type { HealthResponse } from './types'

/** Проверка доступности бэкенда: GET /health (liveness-проба). */
export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health', { signal })
}
