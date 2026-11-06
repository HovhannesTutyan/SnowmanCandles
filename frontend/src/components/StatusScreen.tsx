import type { ReactNode } from 'react'

import { useI18n } from '../i18n/context'
import { LogoIcon } from './icons'
import styles from './StatusScreen.module.css'

/** "full": covers the window (before the site loads). "page": inside the layout. */
type Variant = 'full' | 'page'

export function LoadingScreen({ variant = 'full' }: { variant?: Variant }) {
  const { t } = useI18n()
  return (
    <div className={`${styles.screen} ${styles[variant]}`} role="status" aria-live="polite">
      <span className={styles.logo}>
        <LogoIcon size={56} />
      </span>
      <span className="visually-hidden">{t.status.loading}</span>
    </div>
  )
}

interface ErrorScreenProps {
  error: Error
  onRetry: () => void
  variant?: Variant
}

export function ErrorScreen({ error, onRetry, variant = 'full' }: ErrorScreenProps) {
  const { t } = useI18n()
  return (
    <MessageScreen
      variant={variant}
      role="alert"
      title={t.status.loadFailed}
      action={
        <button type="button" className={styles.button} onClick={onRetry}>
          {t.status.tryAgain}
        </button>
      }
    >
      {t.status.checkConnection}
      {import.meta.env.DEV && (
        <>
          <br />
          <small className={styles.detail}>
            {error.message} Is the Django server running on port 8000?
          </small>
        </>
      )}
    </MessageScreen>
  )
}

interface MessageScreenProps {
  title: string
  children: ReactNode
  action?: ReactNode
  variant?: Variant
  role?: 'alert' | 'status'
}

/** A centred message with an optional action (errors, "not found"). */
export function MessageScreen({
  title,
  children,
  action,
  variant = 'page',
  role,
}: MessageScreenProps) {
  return (
    <div className={`${styles.screen} ${styles[variant]}`} role={role}>
      <LogoIcon size={48} />
      <h1 className={styles.title}>{title}</h1>
      <p className={styles.text}>{children}</p>
      {action}
    </div>
  )
}
