
import { MessageScreen } from '../components/StatusScreen'
import { PageHead } from '../components/layout/PageHead'
import { useI18n } from '../i18n/context'
import { Link } from '../i18n/Link'
import styles from './NotFoundPage.module.css'

interface NotFoundPageProps {
  title?: string
  message?: string
}

export function NotFoundPage({ title, message }: NotFoundPageProps) {
  const { t } = useI18n()
  const heading = title ?? t.status.notFoundTitle
  return (
    <>
      <PageHead title={heading} />
      <MessageScreen
        title={heading}
        action={
          <Link to="/#winter" className={styles.button}>
            {t.status.browse}
          </Link>
        }
      >
        {message ?? t.status.notFoundText}
      </MessageScreen>
    </>
  )
}
