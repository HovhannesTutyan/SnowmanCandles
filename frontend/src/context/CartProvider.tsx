import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { CartContext, type CartLine } from './cart'

const STORAGE_KEY = 'candle-shop:cart'

function readStoredLines(): CartLine[] {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
    return Array.isArray(parsed)
      ? parsed.filter(
          (line): line is CartLine =>
            typeof line?.key === 'string' && Number.isInteger(line?.quantity) && line.quantity > 0,
        )
      : []
  } catch {
    return [] // storage blocked or corrupted
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(readStoredLines)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lines))
    } catch {
      // Private mode or full storage: the cart still works for this visit.
    }
  }, [lines])

  const addItem = useCallback((line: CartLine) => {
    setLines((current) => {
      const index = current.findIndex((l) => l.key === line.key && l.scent === line.scent)
      if (index === -1) return [...current, line]
      return current.map((l, i) => (i === index ? { ...l, quantity: l.quantity + line.quantity } : l))
    })
  }, [])

  const value = useMemo(
    () => ({ lines, count: lines.reduce((sum, l) => sum + l.quantity, 0), addItem }),
    [lines, addItem],
  )
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
