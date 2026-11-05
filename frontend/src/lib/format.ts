export type PriceFormatter = (price: string) => string

/** Formats API decimal strings ("24.00") in the shop's currency, e.g. "$24.00". */
export function createPriceFormatter(currency: string, locale = 'en-US'): PriceFormatter {
  let formatter: Intl.NumberFormat | null = null
  try {
    formatter = new Intl.NumberFormat(locale, { style: 'currency', currency })
  } catch {
    // Unknown currency code: fall back to "24.00 XYZ".
  }
  return (price) => {
    const amount = Number(price)
    if (!Number.isFinite(amount)) return price
    return formatter ? formatter.format(amount) : `${amount.toFixed(2)} ${currency}`
  }
}
