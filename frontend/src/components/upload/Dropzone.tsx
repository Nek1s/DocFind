import { useRef, useState } from 'react'
import type { ChangeEvent, DragEvent, KeyboardEvent } from 'react'
import { Icon } from '@/components/ui/Icon'
import { ACCEPT_ATTR } from '@/lib/fileValidation'
import { cn } from '@/lib/cn'
import styles from './Dropzone.module.css'

interface DropzoneProps {
  onFiles: (files: FileList) => void
}

export function Dropzone({ onFiles }: DropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const openPicker = () => inputRef.current?.click()

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (!dragOver) setDragOver(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    // dragleave стреляет и при заходе курсора на дочерние элементы зоны.
    // Сбрасываем подсветку, только когда курсор реально покинул зону.
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setDragOver(false)
    }
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length > 0) onFiles(e.dataTransfer.files)
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) onFiles(e.target.files)
    // сбрасываем, чтобы повторный выбор того же файла снова сработал
    e.target.value = ''
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      openPicker()
    }
  }

  return (
    <div
      className={cn(styles.zone, dragOver && styles.zoneActive)}
      onClick={openPicker}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label="Загрузить файлы: нажмите или перетащите PDF/DOCX"
    >
      <span className={cn(styles.iconWrap, dragOver && styles.iconWrapActive)}>
        <Icon name="Upload" size={26} />
      </span>
      <div className={styles.title}>
        {dragOver ? 'Отпустите файлы здесь' : 'Перетащите документы сюда'}
      </div>
      <div className={styles.subtitle}>PDF или DOCX · до 20 МБ · можно несколько файлов сразу</div>
      <span className={styles.button}>
        <Icon name="Files" size={15} />
        Выбрать файлы
      </span>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT_ATTR}
        onChange={handleChange}
        onClick={(e) => e.stopPropagation()}
        className={styles.input}
      />
    </div>
  )
}
