/** Форматирует размер файла в байтах в строку «2.4 МБ» / «512 КБ». */
export function formatFileSize(bytes: number): string {
  if (!bytes) return '—'
  const mb = bytes / 1024 / 1024
  if (mb >= 1) return `${mb.toFixed(1)} МБ`
  const kb = bytes / 1024
  return `${Math.max(1, Math.round(kb))} КБ`
}
