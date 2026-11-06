import { createContext, useContext } from 'react'

/** The basket, kept in the browser (localStorage) until the order is placed. */
export interface CartLine {
  /** Product key, e.g. "candle-vintage-roadster-candle" (see lib/items.ts). */
  key: string
  scent: string | null
  quantity: number
}

/** Most of one line a visitor can order at once (the API allows the same). */
export const MAX_LINE_QUANTITY = 20

export interface CartContextValue {
  lines: CartLine[]
  /** Number of pieces (sum of quantities), for the header badge. */
  count: number
  /** Adds to the basket (merging with the same product and scent) and opens the basket panel. */
  addItem: (line: CartLine) => void
  /** Sets a line's quantity; 0 removes it. */
  setQuantity: (key: string, scent: string | null, quantity: number) => void
  removeItem: (key: string, scent: string | null) => void
  clear: () => void
  /** The slide-in basket panel. */
  panelOpen: boolean
  openPanel: () => void
  closePanel: () => void
}

export const CartContext = createContext<CartContextValue | null>(null)

export function useCart(): CartContextValue {
  const value = useContext(CartContext)
  if (!value) throw new Error('useCart must be used inside <CartProvider>.')
  return value
}

export function sameLine(line: CartLine, key: string, scent: string | null): boolean {
  return line.key === key && (line.scent ?? '') === (scent ?? '')
}
