/** Результат клиентской валидации файла. */
export type FileStatus = 'valid' | 'error'

/** Активный фильтр списка документов. */
export type UploadFilter = 'all' | 'pdf' | 'docx' | 'error'

/** Файл, выбранный пользователем для загрузки в базу знаний. */
export interface UploadFile {
  id: string
  /** Имя файла с расширением. */
  name: string
  /** Размер в байтах. */
  size: number
  /** Человекочитаемый размер, например «2.4 МБ». */
  sizeLabel: string
  /** Расширение в нижнем регистре: pdf, docx или иное (для невалидных). */
  ext: string
  /** Дата добавления, например «29.06.2026, 14:30». */
  date: string
  status: FileStatus
  /** Текст ошибки, если status === 'error'. */
  error?: string
}
