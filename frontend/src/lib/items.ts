import type { ProductKind, ShopItem, SlideLink } from '../api/types'

export function itemKind(item: Pick<ShopItem, 'product_type'>): ProductKind {
  return item.product_type === 'collection' ? 'collection' : 'candle'
}

/** Candles and collections can share a slug, so prefix it with the kind. */
export function itemKey(item: Pick<ShopItem, 'product_type' | 'slug'>): string {
  return `${itemKind(item)}-${item.slug}`
}

const KIND_PATHS: Record<ProductKind, string> = {
  candle: '/candles',
  collection: '/collections',
}

/** URL of a product page, e.g. "/candles/vintage-roadster-candle". */
export function productPath(kind: ProductKind, slug: string): string {
  return `${KIND_PATHS[kind]}/${slug}`
}

export function itemPath(item: Pick<ShopItem, 'product_type' | 'slug'>): string {
  return productPath(itemKind(item), item.slug)
}

export function slideLinkPath(link: SlideLink): string {
  return productPath(link.type, link.slug)
}

/** The reverse of itemKey: "candle-vintage-roadster-candle" -> candle + slug. */
export function parseItemKey(key: string): { kind: ProductKind; slug: string } | null {
  for (const kind of ['collection', 'candle'] as const) {
    if (key.startsWith(`${kind}-`)) return { kind, slug: key.slice(kind.length + 1) }
  }
  return null
}
