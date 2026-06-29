/** Разрешённые расширения для загрузки в базу знаний. */
export const ALLOWED_EXTENSIONS = ['pdf', 'docx'] as const

/** Максимальный размер файла — 20 МБ. */
export const MAX_FILE_SIZE = 20 * 1024 * 1024

/** Значение для атрибута accept у <input type="file">. */
export const ACCEPT_ATTR = '.pdf,.docx'

export interface ValidationResult {
  ok: boolean
  error?: string
}

/** Возвращает расширение файла в нижнем регистре (без точки). */
export function getExtension(name: string): string {
  const dot = name.lastIndexOf('.')
  return dot >= 0 ? name.slice(dot + 1).toLowerCase() : ''
}

/** Клиентская валидация: разрешены только PDF/DOCX до 20 МБ. */
export function validateFile(file: File): ValidationResult {
  const ext = getExtension(file.name)
  if (!(ALLOWED_EXTENSIONS as readonly string[]).includes(ext)) {
    return { ok: false, error: 'Неверный формат — разрешены PDF и DOCX' }
  }
  if (file.size > MAX_FILE_SIZE) {
    return { ok: false, error: 'Файл превышает 20 МБ' }
  }
  return { ok: true }
}
