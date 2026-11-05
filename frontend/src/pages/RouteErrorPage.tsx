import { useRouteError } from 'react-router'

import { ErrorScreen } from '../components/StatusScreen'

/** Last-resort screen if rendering a page throws. */
export function RouteErrorPage() {
  const error = useRouteError()
  const err = error instanceof Error ? error : new Error('Something went wrong.')
  return <ErrorScreen error={err} onRetry={() => window.location.reload()} />
}
