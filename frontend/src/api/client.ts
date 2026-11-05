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

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    signal,
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new ApiError(response.status, `Request to ${path} failed (${response.status}).`)
  }
  return (await response.json()) as T
}

export function fetchSite(signal?: AbortSignal): Promise<SiteContent> {
  return getJson<SiteContent>('/api/site/', signal)
}

export function fetchHome(signal?: AbortSignal): Promise<HomeData> {
  return getJson<HomeData>('/api/home/', signal)
}

const DETAIL_PATHS: Record<ProductKind, string> = {
  candle: '/api/candles/',
  collection: '/api/collections/',
}

export function fetchProduct(
  kind: ProductKind,
  slug: string,
  signal?: AbortSignal,
): Promise<ProductDetail> {
  return getJson<ProductDetail>(`${DETAIL_PATHS[kind]}${encodeURIComponent(slug)}/`, signal)
}

export function fetchCarePage(signal?: AbortSignal): Promise<CarePageData> {
  return getJson<CarePageData>('/api/care/', signal)
}

export function fetchIngredientsPage(signal?: AbortSignal): Promise<IngredientsPageData> {
  return getJson<IngredientsPageData>('/api/ingredients/', signal)
}

export function fetchDecoratePage(signal?: AbortSignal): Promise<DecoratePageData> {
  return getJson<DecoratePageData>('/api/decorate/', signal)
}
