import type { UploadFilter } from '@/lib/types'
import { cn } from '@/lib/cn'
import styles from './FileFilters.module.css'

interface FileFiltersProps {
  value: UploadFilter
  onChange: (filter: UploadFilter) => void
}

const FILTERS: ReadonlyArray<{ key: UploadFilter; label: string }> = [
  { key: 'all', label: 'Все' },
  { key: 'pdf', label: 'PDF' },
  { key: 'docx', label: 'DOCX' },
  { key: 'error', label: 'Ошибки' },
]

export function FileFilters({ value, onChange }: FileFiltersProps) {
  return (
    <div className={styles.chips}>
      {FILTERS.map((f) => (
        <button
          key={f.key}
          type="button"
          className={cn(styles.chip, value === f.key && styles.chipActive)}
          onClick={() => onChange(f.key)}
          aria-pressed={value === f.key}
        >
          {f.label}
        </button>
      ))}
    </div>
  )
}
