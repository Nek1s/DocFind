import { Icon } from '@/components/ui/Icon'
import { Badge } from '@/components/ui/Badge'
import type { BadgeVariant } from '@/components/ui/Badge'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { cn } from '@/lib/cn'
import type { FileStatus, UploadFile } from '@/lib/types'
import styles from './FileRow.module.css'

interface FileRowProps {
  file: UploadFile
  onRemove: (id: string) => void
}

function fileKind(ext: string): 'pdf' | 'docx' | 'other' {
  if (ext === 'pdf') return 'pdf'
  if (ext === 'docx') return 'docx'
  return 'other'
}

/** Бейдж статуса: вариант оформления + подпись по состоянию обработки. */
function statusBadge(file: UploadFile): { variant: BadgeVariant; label: string } {
  switch (file.status) {
    case 'uploading':
      return { variant: 'info', label: `Загрузка ${Math.round(file.progress ?? 0)}%` }
    case 'indexing':
      return { variant: 'brand', label: 'Индексация' }
    case 'done':
      return { variant: 'success', label: 'Готово' }
    case 'error':
      return { variant: 'danger', label: 'Ошибка' }
  }
}

export function FileRow({ file, onRemove }: FileRowProps) {
  const kind = fileKind(file.ext)
  const extLabel = file.ext ? file.ext.toUpperCase() : 'FILE'
  const badge = statusBadge(file)
  const status: FileStatus = file.status

  return (
    <div className={styles.row}>
      <span className={cn(styles.iconWrap, styles[kind])}>
        <Icon name="File" size={18} />
      </span>

      <div className={styles.main}>
        <div className={styles.nameRow}>
          <span className={styles.name} title={file.name}>
            {file.name}
          </span>
          <span className={cn(styles.ext, styles[kind])}>{extLabel}</span>
        </div>
        <div className={styles.meta}>
          <span className={styles.metaText}>{file.date}</span>
          <span className={styles.dot}>·</span>
          <span className={styles.metaText}>{file.sizeLabel}</span>
        </div>

        {status === 'uploading' && (
          <div className={styles.progress}>
            <ProgressBar value={file.progress ?? 0} color="var(--info)" />
          </div>
        )}
        {status === 'indexing' && (
          <div className={styles.progress}>
            <ProgressBar indeterminate />
          </div>
        )}
        {status === 'error' && file.error && (
          <div className={styles.errorRow}>
            <Icon name="Warning" size={13} />
            <span className={styles.errorText}>{file.error}</span>
          </div>
        )}
      </div>

      <Badge variant={badge.variant}>{badge.label}</Badge>

      <button
        type="button"
        className={styles.remove}
        aria-label={`Удалить файл ${file.name}`}
        onClick={() => onRemove(file.id)}
      >
        <Icon name="Trash" size={16} />
      </button>
    </div>
  )
}
