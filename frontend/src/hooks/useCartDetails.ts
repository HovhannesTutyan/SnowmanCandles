import { useEffect, useMemo, useState } from 'react'

import { fetchCartQuote } from '../api/client'
import type { CartQuoteLine } from '../api/types'
import { MAX_LINE_QUANTITY, useCart, type CartLine } from '../context/cart'
import { useI18n } from '../i18n/context'
import { parseItemKey } from '../lib/items'

/** Why a line can't be ordered as it is. */
export type LineProblem = 'gone' | 'sold_out' | 'too_many'

export interface CartItem {
  line: CartLine
  /** Current product details; undefined while loading, null when it's no longer sold. */
  details: CartQuoteLine | null | undefined
  lineTotal: number
  /** Most the visitor can choose for this line. */
  maxQuantity: number
  problem: LineProblem | null
}

export interface CartDetails {
  items: CartItem[]
  subtotal: number
  /** True until the first details arrive. */
  loading: boolean
  error: boolean
  retry: () => void
  /** Forget the loaded details and fetch them again (e.g. after stock changed). */
  refresh: () => void
  /** Every line has details and enough stock. */
  canCheckout: boolean
}

const lineId = (line: Pick<CartLine, 'key' | 'scent'>) => `${line.key}|${line.scent ?? ''}`
const NO_DETAILS: Record<string, CartQuoteLine | null> = {}

/**
 * The basket lines joined with their current price, title, image and stock from the API.
 * Details are fetched per product (not per quantity), so changing a quantity doesn't
 * refetch; earlier details stay on screen while a new product loads.
 */
export function useCartDetails(): CartDetails {
  const { lines } = useCart()
  const { locale } = useI18n()
  const [known, setKnown] = useState<{ locale: string; byId: Record<string, CartQuoteLine | null> }>({
    locale,
    byId: {},
  })
  const [error, setError] = useState(false)
  const [attempt, setAttempt] = useState(0)

  // Products whose details we don't have yet (in this language).
  const byId = known.locale === locale ? known.byId : NO_DETAILS
  const missing = lines.filter((line) => !(lineId(line) in byId))
  const missingKey = missing.length ? JSON.stringify(missing.map(lineId).sort()) : ''

  useEffect(() => {
    if (!missingKey) return
    const wanted = (JSON.parse(missingKey) as string[]).map((id) => {
      const split = id.indexOf('|')
      return { id, key: id.slice(0, split), scent: id.slice(split + 1) }
    })
    const items = wanted.flatMap(({ key, scent }) => {
      const parsed = parseItemKey(key)
      return parsed ? [{ ...parsed, scent }] : []
    })
    const controller = new AbortController()
    fetchCartQuote(items, locale, controller.signal)
      .then((quote) => {
        // An empty or unexpected answer (e.g. while the server restarts) is a load error,
        // shown with "Try again", never a crash.
        if (!Array.isArray(quote?.lines)) throw new Error('Unexpected basket answer.')
        // Worked out here, not inside the state updater, so nothing can throw while rendering.
        const found: Record<string, CartQuoteLine | null> = {}
        let i = 0
        for (const { id, key } of wanted) {
          found[id] = parseItemKey(key) ? (quote.lines[i++] ?? null) : null
        }
        setError(false)
        setKnown((current) => ({
          locale,
          byId: { ...(current.locale === locale ? current.byId : {}), ...found },
        }))
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true)
      })
    return () => controller.abort()
  }, [missingKey, locale, attempt])

  return useMemo(() => {
    const items: CartItem[] = lines.map((line) => {
      const id = lineId(line)
      const details = id in byId ? byId[id] : undefined
      const price = details ? Number(details.price) : 0
      const maxQuantity = details ? Math.max(1, Math.min(details.stock, MAX_LINE_QUANTITY)) : MAX_LINE_QUANTITY
      let problem: LineProblem | null = null
      if (details === null) problem = 'gone'
      else if (details && details.stock <= 0) problem = 'sold_out'
      else if (details && line.quantity > details.stock) problem = 'too_many'
      return { line, details, lineTotal: price * line.quantity, maxQuantity, problem }
    })
    const subtotal = items.reduce((sum, item) => sum + (item.problem ? 0 : item.lineTotal), 0)
    return {
      items,
      subtotal,
      loading: items.some((item) => item.details === undefined) && !error,
      error,
      retry: () => setAttempt((n) => n + 1),
      refresh: () => setKnown({ locale, byId: {} }),
      canCheckout: items.length > 0 && items.every((item) => item.details && !item.problem),
    }
  }, [lines, byId, error, locale])
}
