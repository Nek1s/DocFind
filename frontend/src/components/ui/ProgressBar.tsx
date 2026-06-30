import styles from './ProgressBar.module.css'

interface ProgressBarProps {
  /** Прогресс 0–100. Игнорируется при indeterminate. */
  value?: number
  /** Неопределённый режим — бегущий сегмент вместо заполнения по value. */
  indeterminate?: boolean
  /** Цвет заполнения (CSS-переменная), по умолчанию синий «info». */
  color?: string
}

/**
 * Полоса прогресса для строки документа.
 * - determinate: ширина = value%, цвет из color (загрузка файла);
 * - indeterminate: бегущий сегмент, когда прогресс неизвестен (индексация).
 */
export function ProgressBar({ value = 0, indeterminate = false, color = 'var(--info)' }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value))

  return (
    <div
      className={styles.track}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={indeterminate ? undefined : Math.round(clamped)}
    >
      {indeterminate ? (
        <div className={styles.indeterminate} />
      ) : (
        <div className={styles.fill} style={{ width: `${clamped}%`, background: color }} />
      )}
    </div>
  )
}
