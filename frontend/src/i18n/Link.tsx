import { Link as RouterLink, type LinkProps } from 'react-router'

import { useI18n } from './context'

/**
 * React Router's <Link>, staying in the current language: to="/candle-care" goes to
 * "/candle-care" in Armenian, "/en/candle-care" in English and "/ru/candle-care" in Russian.
 */
export function Link({ to, ...props }: LinkProps) {
  const { path } = useI18n()
  return <RouterLink to={typeof to === 'string' ? path(to) : to} {...props} />
}
