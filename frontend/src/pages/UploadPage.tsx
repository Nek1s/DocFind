import { useMemo, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import type { UseUploadFiles } from '@/hooks/useUploadFiles'
import type { UploadFilter } from '@/lib/types'
import { Dropzone } from '@/components/upload/Dropzone'
import { UploadStats } from '@/components/upload/UploadStats'
import { FileFilters } from '@/components/upload/FileFilters'
import { FileList } from '@/components/upload/FileList'
import styles from './UploadPage.module.css'

export function UploadPage() {
  const { files, addFiles, removeFile } = useOutletContext<UseUploadFiles>()
  const [filter, setFilter] = useState<UploadFilter>('all')

  const counts = useMemo(
    () => ({
      total: files.length,
      valid: files.filter((f) => f.status === 'valid').length,
      error: files.filter((f) => f.status === 'error').length,
    }),
    [files],
  )

  const filtered = useMemo(() => {
    switch (filter) {
      case 'error':
        return files.filter((f) => f.status === 'error')
      case 'pdf':
        return files.filter((f) => f.ext === 'pdf')
      case 'docx':
        return files.filter((f) => f.ext === 'docx')
      default:
        return files
    }
  }, [files, filter])

  return (
    <div className={styles.view}>
      <Dropzone onFiles={addFiles} />
      <UploadStats total={counts.total} valid={counts.valid} error={counts.error} />
      <div className={styles.toolbar}>
        <span className={styles.toolbarLabel}>ДОКУМЕНТЫ</span>
        <FileFilters value={filter} onChange={setFilter} />
      </div>
      <FileList files={filtered} totalCount={files.length} onRemove={removeFile} />
    </div>
  )
}
