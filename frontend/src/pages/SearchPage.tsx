import { Icon } from '@/components/ui/Icon'
import styles from './SearchPage.module.css'

export function SearchPage() {
  return (
    <div className={styles.view}>
      <div className={styles.placeholder}>
        <span className={styles.icon}>
          <Icon name="Search" size={24} />
        </span>
        <div className={styles.title}>Поиск скоро появится</div>
        <div className={styles.hint}>
          Полнотекстовый поиск по загруженным документам — в следующей задаче. Пока загрузите PDF
          или DOCX на вкладке «Загрузка».
        </div>
      </div>
    </div>
  )
}
