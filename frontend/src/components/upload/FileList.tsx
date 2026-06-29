import { Icon } from '@/components/ui/Icon'
import type { UploadFile } from '@/lib/types'
import { FileRow } from './FileRow'
import styles from './FileList.module.css'

interface FileListProps {
  /** Файлы после применения фильтра. */
  files: UploadFile[]
  /** Общее число файлов (до фильтра) — чтобы отличить пустой фильтр от пустого списка. */
  totalCount: number
  onRemove: (id: string) => void
}

export function FileList({ files, totalCount, onRemove }: FileListProps) {
  if (files.length === 0) {
    const noFilesAtAll = totalCount === 0
    return (
      <div className={styles.empty}>
        <span className={styles.emptyIcon}>
          <Icon name="Folder" size={22} />
        </span>
        <div className={styles.emptyTitle}>
          {noFilesAtAll ? 'Пока нет документов' : 'Нет документов в этом фильтре'}
        </div>
        <div className={styles.emptyHint}>
          {noFilesAtAll
            ? 'Перетащите PDF или DOCX в зону выше, чтобы начать.'
            : 'Смените фильтр или загрузите новые файлы.'}
        </div>
      </div>
    )
  }

  return (
    <div className={styles.list}>
      {files.map((file) => (
        <FileRow key={file.id} file={file} onRemove={onRemove} />
      ))}
    </div>
  )
}
