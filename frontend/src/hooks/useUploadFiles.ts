import { useCallback, useEffect, useRef, useState } from 'react'
import type { FileStatus, UploadFile } from '@/lib/types'
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

// Параметры симуляции обработки на сервере (бэкенда под статусы пока нет).
const TICK_MS = 150 // частота обновления прогресса
const INDEXING_TICKS = 8 // длительность фазы индексации в тиках (≈1.2 c)

export interface UseUploadFiles {
  files: UploadFile[]
  addFiles: (list: FileList | File[]) => void
  removeFile: (id: string) => void
  clearFiles: () => void
}

/**
 * Хранит список документов и моделирует их обработку на сервере.
 *
 * Валидный файл проходит пайплайн uploading → indexing → done; невалидный
 * (формат/размер) сразу получает status 'error'. Прогресс «загрузки» и
 * «индексации» симулируется таймерами — реального бэкенда под статусы ещё нет.
 * Дубликаты (по имени + размеру) повторно не добавляются.
 */
export function useUploadFiles(): UseUploadFiles {
  const [files, setFiles] = useState<UploadFile[]>([])
  // Активные таймеры симуляции по id файла — чтобы гасить их при удалении/размонтировании.
  const timers = useRef<Record<string, ReturnType<typeof setInterval>>>({})

  const patch = useCallback((id: string, upd: Partial<UploadFile>) => {
    setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, ...upd } : f)))
  }, [])

  const stopTimer = useCallback((id: string) => {
    const timer = timers.current[id]
    if (timer !== undefined) {
      clearInterval(timer)
      delete timers.current[id]
    }
  }, [])

  // Запускает имитацию обработки одного файла: разгон прогресса до 100%,
  // затем фаза индексации, затем готово.
  const simulate = useCallback(
    (id: string) => {
      let phase: Extract<FileStatus, 'uploading' | 'indexing'> = 'uploading'
      let progress = 0
      let indexTicks = 0

      stopTimer(id)
      timers.current[id] = setInterval(() => {
        if (phase === 'uploading') {
          progress = Math.min(100, progress + Math.random() * 15 + 7)
          if (progress >= 100) {
            phase = 'indexing'
            patch(id, { status: 'indexing', progress: 100 })
          } else {
            patch(id, { status: 'uploading', progress })
          }
        } else {
          indexTicks += 1
          if (indexTicks > INDEXING_TICKS) {
            patch(id, { status: 'done', progress: 100 })
            stopTimer(id)
          }
        }
      }, TICK_MS)
    },
    [patch, stopTimer],
  )

  const addFiles = useCallback((list: FileList | File[]) => {
    const incoming = Array.from(list)
    if (incoming.length === 0) return

    // Готовим записи ОДИН раз снаружи: генерация id и валидация — это побочные
    // эффекты, им не место в updater'е (StrictMode вызывает его дважды).
    const prepared = incoming.map((file) => {
      const result = validateFile(file)
      const base = {
        id: nextId(),
        name: file.name,
        size: file.size,
        sizeLabel: formatFileSize(file.size),
        ext: getExtension(file.name),
        date: nowLabel(),
      }
      const entry: UploadFile = result.ok
        ? { ...base, status: 'uploading', progress: 0 }
        : { ...base, status: 'error', error: result.error }
      return { key: `${file.name}:${file.size}`, entry }
    })

    // Updater чистый: только дедуп против prev и склейка. Запуск симуляции —
    // в useEffect ниже, как реакция на состояние, а не на событие.
    setFiles((prev) => {
      const seen = new Set(prev.map((f) => `${f.name}:${f.size}`))
      const created: UploadFile[] = []
      for (const { key, entry } of prepared) {
        if (seen.has(key)) continue
        seen.add(key)
        created.push(entry)
      }
      return [...created, ...prev]
    })
  }, [])

  const removeFile = useCallback(
    (id: string) => {
      stopTimer(id)
      setFiles((prev) => prev.filter((f) => f.id !== id))
    },
    [stopTimer],
  )

  const clearFiles = useCallback(() => {
    Object.keys(timers.current).forEach(stopTimer)
    setFiles([])
  }, [stopTimer])

  // Запускаем симуляцию для каждого нового файла в статусе uploading, у которого
  // ещё нет таймера. Реакция на состояние (а не на событие addFiles) делает это
  // устойчивым к повторному вызову updater'а в StrictMode.
  useEffect(() => {
    for (const f of files) {
      if (f.status === 'uploading' && timers.current[f.id] === undefined) {
        simulate(f.id)
      }
    }
  }, [files, simulate])

  // Гасим все таймеры при размонтировании.
  useEffect(() => {
    const active = timers.current
    return () => {
      Object.values(active).forEach(clearInterval)
    }
  }, [])

  return { files, addFiles, removeFile, clearFiles }
}
