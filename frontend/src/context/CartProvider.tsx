import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { CartContext, MAX_LINE_QUANTITY, sameLine, type CartLine } from './cart'

const STORAGE_KEY = 'candle-shop:cart'

function readStoredLines(): CartLine[] {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
    return Array.isArray(parsed)
      ? parsed
          .filter(
            (line): line is CartLine =>
              typeof line?.key === 'string' && Number.isInteger(line?.quantity) && line.quantity > 0,
          )
          .map((line) => ({ ...line, quantity: Math.min(line.quantity, MAX_LINE_QUANTITY) }))
      : []
  } catch {
    return [] // storage blocked or corrupted
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(readStoredLines)
  const [panelOpen, setPanelOpen] = useState(false)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lines))
    } catch {
      // Private mode or full storage: the cart still works for this visit.
    }
  }, [lines])

  const addItem = useCallback((line: CartLine) => {
    setLines((current) => {
      const index = current.findIndex((l) => sameLine(l, line.key, line.scent))
      if (index === -1) return [...current, { ...line, quantity: Math.min(line.quantity, MAX_LINE_QUANTITY) }]
      return current.map((l, i) =>
        i === index ? { ...l, quantity: Math.min(l.quantity + line.quantity, MAX_LINE_QUANTITY) } : l,
      )
    })
    setPanelOpen(true)
  }, [])

  const setQuantity = useCallback((key: string, scent: string | null, quantity: number) => {
    setLines((current) =>
      quantity <= 0
        ? current.filter((l) => !sameLine(l, key, scent))
        : current.map((l) =>
            sameLine(l, key, scent) ? { ...l, quantity: Math.min(quantity, MAX_LINE_QUANTITY) } : l,
          ),
    )
  }, [])

  const removeItem = useCallback((key: string, scent: string | null) => {
    setLines((current) => current.filter((l) => !sameLine(l, key, scent)))
  }, [])

  const clear = useCallback(() => setLines([]), [])
  const openPanel = useCallback(() => setPanelOpen(true), [])
  const closePanel = useCallback(() => setPanelOpen(false), [])

  const value = useMemo(
    () => ({
      lines,
      count: lines.reduce((sum, l) => sum + l.quantity, 0),
      addItem,
      setQuantity,
      removeItem,
      clear,
      panelOpen,
      openPanel,
      closePanel,
    }),
    [lines, addItem, setQuantity, removeItem, clear, panelOpen, openPanel, closePanel],
  )
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
