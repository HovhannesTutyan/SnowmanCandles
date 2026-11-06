import { useMemo, type ReactNode } from 'react'

import type { SiteContent } from '../api/types'
import { useI18n } from '../i18n/context'
import { createPriceFormatter } from '../lib/format'
import { SiteContext } from './site'

export function SiteProvider({ content, children }: { content: SiteContent; children: ReactNode }) {
  const { intlLocale } = useI18n()
  const value = useMemo(
    () => ({ content, formatPrice: createPriceFormatter(content.currency, intlLocale) }),
    [content, intlLocale],
  )
  return <SiteContext.Provider value={value}>{children}</SiteContext.Provider>
}
