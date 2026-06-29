import { NavLink } from 'react-router-dom'
import { Icon } from '@/components/ui/Icon'
import { cn } from '@/lib/cn'
import styles from './AppHeader.module.css'

interface AppHeaderProps {
  docCount: number
}

export function AppHeader({ docCount }: AppHeaderProps) {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <span className={styles.logo}>
          <Icon name="Knowledge" size={19} />
        </span>
        <div className={styles.brandText}>
          <div className={styles.brandTitle}>База знаний</div>
          <div className={styles.brandSubtitle}>Интеллектуальный поиск по документам</div>
        </div>
      </div>

      <nav className={styles.tabs}>
        <NavLink
          to="/upload"
          className={({ isActive }) => cn(styles.tab, isActive && styles.tabActive)}
        >
          <Icon name="Upload" size={14} />
          Загрузка
        </NavLink>
        <NavLink
          to="/search"
          className={({ isActive }) => cn(styles.tab, isActive && styles.tabActive)}
        >
          <Icon name="Search" size={14} />
          Поиск
        </NavLink>
      </nav>

      <div className={styles.meta}>
        <span className={styles.count}>{docCount} док.</span>
        <span className={styles.avatar}>АК</span>
      </div>
    </header>
  )
}
