import { cn } from '@/lib/cn'
import styles from './UploadStats.module.css'

interface UploadStatsProps {
  total: number
  valid: number
  error: number
}

export function UploadStats({ total, valid, error }: UploadStatsProps) {
  const plates = [
    { key: 'total', value: total, label: 'всего', tone: styles.total },
    { key: 'valid', value: valid, label: 'готово', tone: styles.valid },
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
