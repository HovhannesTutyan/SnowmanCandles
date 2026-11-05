import { Link } from 'react-router'

import { MessageScreen } from '../components/StatusScreen'
import styles from './NotFoundPage.module.css'

interface NotFoundPageProps {
  title?: string
  message?: string
}

export function NotFoundPage({
  title = "This page doesn't exist",
  message = 'The link may be old, or the address mistyped.',
}: NotFoundPageProps) {
  return (
    <>
      <title>{title}</title>
      <MessageScreen
        title={title}
        action={
          <Link to="/#winter" className={styles.button}>
            Browse the collection
          </Link>
        }
      >
        {message}
      </MessageScreen>
    </>
  )
}
