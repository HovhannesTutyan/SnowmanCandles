import { createBrowserRouter, type RouteObject } from 'react-router'

import { SiteLayout } from './components/layout/SiteLayout'
import { LocaleRoot } from './i18n/LocaleRoot'
import { LOCALE_PREFIX, LOCALES } from './i18n/locales'
import { BasketPage } from './pages/BasketPage'
import { CareTipsPage } from './pages/CareTipsPage'
import { CheckoutPage } from './pages/CheckoutPage'
import { DecoratePage } from './pages/DecoratePage'
import { HomePage } from './pages/HomePage'
import { IngredientsPage } from './pages/IngredientsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ProductPage } from './pages/ProductPage'
import { RouteErrorPage } from './pages/RouteErrorPage'

const pages: RouteObject[] = [
  { index: true, element: <HomePage /> },
  { path: 'candles/:slug', element: <ProductPage kind="candle" /> },
  { path: 'collections/:slug', element: <ProductPage kind="collection" /> },
  { path: 'candle-care', element: <CareTipsPage /> },
  { path: 'ingredients', element: <IngredientsPage /> },
  { path: 'decorate', element: <DecoratePage /> },
  { path: 'basket', element: <BasketPage /> },
  { path: 'checkout', element: <CheckoutPage /> },
  { path: '*', element: <NotFoundPage /> },
]

/** The same pages under each language: "/" (Armenian), "/en/…" and "/ru/…". */
export const routes: RouteObject[] = LOCALES.map((locale) => ({
  path: LOCALE_PREFIX[locale] || '/',
  element: <LocaleRoot locale={locale} />,
  children: [{ element: <SiteLayout />, errorElement: <RouteErrorPage />, children: pages }],
}))

export const router = createBrowserRouter(routes)
