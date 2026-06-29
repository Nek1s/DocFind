import type { CSSProperties } from 'react'
import { ICON_DATA } from './iconData'
import type { IconName } from './iconData'

interface IconProps {
  name: IconName
  size?: number
  className?: string
  style?: CSSProperties
}

/**
 * Рендерит глиф из набора Claude Design System. Данные статичны и доверены
 * (извлечены из дизайн-системы), поэтому dangerouslySetInnerHTML безопасен.
 */
export function Icon({ name, size = 20, className, style }: IconProps) {
  const glyph = ICON_DATA[name]
  return (
    <svg
      width={size}
      height={size}
      viewBox={glyph.viewBox}
      fill="none"
      className={className}
      style={style}
      role="presentation"
      aria-hidden="true"
      dangerouslySetInnerHTML={{ __html: glyph.body }}
    />
  )
}
