import { Outlet } from 'react-router-dom'
import { useUploadFiles } from '@/hooks/useUploadFiles'
import { AppHeader } from './AppHeader'
import styles from './RootLayout.module.css'

export function RootLayout() {
  const upload = useUploadFiles()

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.card}>
          <AppHeader docCount={upload.files.length} />
          <Outlet context={upload} />
        </div>
        <div className={styles.footer}>База знаний · загрузка документов PDF и DOCX</div>
      </div>
    </div>
  )
}
