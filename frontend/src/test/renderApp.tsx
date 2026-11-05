import { render } from '@testing-library/react'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { vi } from 'vitest'

import { CartProvider } from '../context/CartProvider'
import { routes } from '../router'

type Responses = Record<string, unknown>

/**
 * Mocks fetch by API path: a value is returned as JSON (200), a number is used as
 * an error status, and unknown paths return 404.
 */
export function mockApi(responses: Responses) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const path = new URL(String(input), 'http://localhost').pathname
    const body = responses[path]
    if (body === undefined) return new Response('{}', { status: 404 })
    if (typeof body === 'number') return new Response('{}', { status: body })
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  })
}

/** Renders the whole app (layout, routes, cart) at `path`. */
export function renderApp(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  return { router, ...render(<CartProvider><RouterProvider router={router} /></CartProvider>) }
}
