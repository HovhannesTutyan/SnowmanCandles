import { useMemo, type ReactNode } from 'react'

import type { SiteContent } from '../api/types'
import { createPriceFormatter } from '../lib/format'
import { SiteContext } from './site'

export function SiteProvider({ content, children }: { content: SiteContent; children: ReactNode }) {
  const value = useMemo(
    () => ({ content, formatPrice: createPriceFormatter(content.currency) }),
    [content],
  )
  return <SiteContext.Provider value={value}>{children}</SiteContext.Provider>
}
