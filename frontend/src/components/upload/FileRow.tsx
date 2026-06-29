import { Icon } from '@/components/ui/Icon'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/cn'
import type { UploadFile } from '@/lib/types'
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

export function FileRow({ file, onRemove }: FileRowProps) {
  const kind = fileKind(file.ext)
  const extLabel = file.ext ? file.ext.toUpperCase() : 'FILE'
  const isError = file.status === 'error'

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
        {isError && file.error && (
          <div className={styles.errorRow}>
            <Icon name="Warning" size={13} />
            <span className={styles.errorText}>{file.error}</span>
          </div>
        )}
      </div>

      <Badge variant={isError ? 'danger' : 'success'}>
        {isError ? 'Ошибка' : 'Готов к загрузке'}
      </Badge>

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
