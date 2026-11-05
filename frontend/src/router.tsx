import { createBrowserRouter, type RouteObject } from 'react-router'

import { SiteLayout } from './components/layout/SiteLayout'
import { CareTipsPage } from './pages/CareTipsPage'
import { DecoratePage } from './pages/DecoratePage'
import { HomePage } from './pages/HomePage'
import { IngredientsPage } from './pages/IngredientsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ProductPage } from './pages/ProductPage'
import { RouteErrorPage } from './pages/RouteErrorPage'

export const routes: RouteObject[] = [
  {
    element: <SiteLayout />,
    errorElement: <RouteErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'candles/:slug', element: <ProductPage kind="candle" /> },
      { path: 'collections/:slug', element: <ProductPage kind="collection" /> },
      { path: 'candle-care', element: <CareTipsPage /> },
      { path: 'ingredients', element: <IngredientsPage /> },
      { path: 'decorate', element: <DecoratePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]

export const router = createBrowserRouter(routes)
