import { useRouteError } from 'react-router'

import { ErrorScreen } from '../components/StatusScreen'
import { useI18n } from '../i18n/context'

/** Last-resort screen if rendering a page throws. */
export function RouteErrorPage() {
  const error = useRouteError()
  const { t } = useI18n()
  const err = error instanceof Error ? error : new Error(t.status.somethingWrong)
  return <ErrorScreen error={err} onRetry={() => window.location.reload()} />
}
