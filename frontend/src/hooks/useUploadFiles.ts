import { useCallback, useState } from 'react'
import type { UploadFile } from '@/lib/types'
import { getExtension, validateFile } from '@/lib/fileValidation'
import { formatFileSize } from '@/lib/formatFileSize'

function nowLabel(): string {
  const d = new Date()
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()}, ${p(d.getHours())}:${p(d.getMinutes())}`
}

let idCounter = 0
function nextId(): string {
  idCounter += 1
  return `file-${Date.now().toString(36)}-${idCounter}`
}

export interface UseUploadFiles {
  files: UploadFile[]
  addFiles: (list: FileList | File[]) => void
  removeFile: (id: string) => void
  clearFiles: () => void
}

/**
 * Хранит список выбранных пользователем файлов. Каждый файл проходит
 * клиентскую валидацию (PDF/DOCX, ≤20 МБ) и получает статус valid/error.
 * Дубликаты (по имени + размеру) повторно не добавляются.
 */
export function useUploadFiles(): UseUploadFiles {
  const [files, setFiles] = useState<UploadFile[]>([])

  const addFiles = useCallback((list: FileList | File[]) => {
    const incoming = Array.from(list)
    if (incoming.length === 0) return

    setFiles((prev) => {
      const seen = new Set(prev.map((f) => `${f.name}:${f.size}`))
      const created: UploadFile[] = []

      for (const file of incoming) {
        const key = `${file.name}:${file.size}`
        if (seen.has(key)) continue
        seen.add(key)

        const result = validateFile(file)
        created.push({
          id: nextId(),
          name: file.name,
          size: file.size,
          sizeLabel: formatFileSize(file.size),
          ext: getExtension(file.name),
          date: nowLabel(),
          status: result.ok ? 'valid' : 'error',
          error: result.error,
        })
      }

      return [...created, ...prev]
    })
  }, [])

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }, [])

  const clearFiles = useCallback(() => setFiles([]), [])

  return { files, addFiles, removeFile, clearFiles }
}
