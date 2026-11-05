import { createContext, useContext } from 'react'

/**
 * A simple cart kept in the browser. There's no cart page or checkout yet: it
 * powers the header badge, and the lines are ready for a checkout later.
 */
export interface CartLine {
  /** Product key, e.g. "candle-vintage-roadster-candle" (see lib/items.ts). */
  key: string
  scent: string | null
  quantity: number
}

export interface CartContextValue {
  lines: CartLine[]
  count: number
  addItem: (line: CartLine) => void
}

export const CartContext = createContext<CartContextValue | null>(null)

export function useCart(): CartContextValue {
  const value = useContext(CartContext)
  if (!value) throw new Error('useCart must be used inside <CartProvider>.')
  return value
}
