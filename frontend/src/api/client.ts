import type { Locale } from '../i18n/locales'
import type {
  CarePageData,
  DecoratePageData,
  HomeData,
  IngredientsPageData,
  ProductDetail,
  ProductKind,
  SiteContent,
} from './types'

/** Empty in development: Vite proxies /api and /media to Django. */
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
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
