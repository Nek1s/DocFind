import { cn } from '@/lib/cn'
import styles from './UploadStats.module.css'

interface UploadStatsProps {
  total: number
  done: number
  /** Файлы в обработке: uploading + indexing. */
  processing: number
  error: number
}

export function UploadStats({ total, done, processing, error }: UploadStatsProps) {
  const plates = [
    { key: 'total', value: total, label: 'всего', tone: styles.total },
    { key: 'done', value: done, label: 'готово', tone: styles.done },
    { key: 'processing', value: processing, label: 'в обработке', tone: styles.processing },
    { key: 'error', value: error, label: 'с ошибкой', tone: styles.error },
  ]

  return (
    <div className={styles.strip}>
      {plates.map((p) => (
        <div key={p.key} className={styles.plate}>
          <div className={cn(styles.value, p.tone)}>{p.value}</div>
          <div className={styles.label}>{p.label}</div>
        </div>
      ))}
    </div>
  )
}
