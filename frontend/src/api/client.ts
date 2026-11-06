import type { Locale } from '../i18n/locales'
import type {
  CartQuote,
  CarePageData,
  DecoratePageData,
  HomeData,
  IngredientsPageData,
  OrderRequest,
  OutOfStockProblem,
  PlacedOrder,
  ProductDetail,
  ProductKind,
  SiteContent,
} from './types'

/** Empty in development: Vite proxies /api and /media to Django. */
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number
  /** The JSON error body, when there is one (e.g. field errors). */
  readonly body: unknown

  constructor(status: number, message: string, body: unknown = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

export function isNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.status === 404
}

/** GET an API path in `locale`: translated texts come back in that language. */
async function getJson<T>(path: string, locale: Locale, signal?: AbortSignal): Promise<T> {
  const url = `${API_BASE_URL}${path}${path.includes('?') ? '&' : '?'}lang=${locale}`
  const response = await fetch(url, {
    signal,
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new ApiError(response.status, `Request to ${path} failed (${response.status}).`)
  }
  return (await response.json()) as T
}

export function fetchSite(locale: Locale, signal?: AbortSignal): Promise<SiteContent> {
  return getJson<SiteContent>('/api/site/', locale, signal)
}

export function fetchHome(locale: Locale, signal?: AbortSignal): Promise<HomeData> {
  return getJson<HomeData>('/api/home/', locale, signal)
}

const DETAIL_PATHS: Record<ProductKind, string> = {
  candle: '/api/candles/',
  collection: '/api/collections/',
}

export function fetchProduct(
  kind: ProductKind,
  slug: string,
  locale: Locale,
  signal?: AbortSignal,
): Promise<ProductDetail> {
  return getJson<ProductDetail>(`${DETAIL_PATHS[kind]}${encodeURIComponent(slug)}/`, locale, signal)
}

export function fetchCarePage(locale: Locale, signal?: AbortSignal): Promise<CarePageData> {
  return getJson<CarePageData>('/api/care/', locale, signal)
}

export function fetchIngredientsPage(locale: Locale, signal?: AbortSignal): Promise<IngredientsPageData> {
  return getJson<IngredientsPageData>('/api/ingredients/', locale, signal)
}

export function fetchDecoratePage(locale: Locale, signal?: AbortSignal): Promise<DecoratePageData> {
  return getJson<DecoratePageData>('/api/decorate/', locale, signal)
}

async function postJson<T>(path: string, locale: Locale, body: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}?lang=${locale}`, {
    method: 'POST',
    signal,
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  let data: unknown = null
  try {
    data = await response.json()
  } catch {
    // no JSON body
  }
  if (!response.ok) {
    throw new ApiError(response.status, `Request to ${path} failed (${response.status}).`, data)
  }
  return data as T
}

/** Current titles, images, prices and stock for basket products (quantity 1 each). */
export function fetchCartQuote(
  items: { kind: ProductKind; slug: string; scent: string }[],
  locale: Locale,
  signal?: AbortSignal,
): Promise<CartQuote> {
  return postJson<CartQuote>(
    '/api/cart/',
    locale,
    { items: items.map((item) => ({ ...item, quantity: 1 })) },
    signal,
  )
}

export function placeOrder(order: OrderRequest, locale: Locale): Promise<PlacedOrder> {
  return postJson<PlacedOrder>('/api/orders/', locale, order)
}

/** The lines a 409 "out of stock" answer points at, or null for any other error. */
export function outOfStockProblems(error: unknown): OutOfStockProblem[] | null {
  if (!(error instanceof ApiError) || error.status !== 409) return null
  const body = error.body as { problems?: OutOfStockProblem[] } | null
  return body?.problems ?? []
}
