/**
 * Repeats `items` until there are at least `minLength` of them, so the endless
 * marquees (ticker, product train) never show a gap on wide screens.
 */
export function repeatToLength<T>(items: readonly T[], minLength: number): T[] {
  if (items.length === 0) return []
  const result = [...items]
  while (result.length < minLength) result.push(...items)
  return result
}
