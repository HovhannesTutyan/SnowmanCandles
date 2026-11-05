import { createContext, useContext } from 'react'

import type { SiteContent } from '../api/types'
import type { PriceFormatter } from '../lib/format'

export interface SiteContextValue {
  content: SiteContent
  formatPrice: PriceFormatter
}

export const SiteContext = createContext<SiteContextValue | null>(null)

/** Site-wide texts from the admin, plus a price formatter in the shop's currency. */
export function useSite(): SiteContextValue {
  const value = useContext(SiteContext)
  if (!value) throw new Error('useSite must be used inside <SiteProvider>.')
  return value
}
