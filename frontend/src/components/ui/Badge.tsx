import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import styles from './Badge.module.css'

export type BadgeVariant = 'success' | 'danger' | 'info' | 'brand'

interface BadgeProps {
  variant: BadgeVariant
  children: ReactNode
}

export function Badge({ variant, children }: BadgeProps) {
  return <span className={cn(styles.badge, styles[variant])}>{children}</span>
}
