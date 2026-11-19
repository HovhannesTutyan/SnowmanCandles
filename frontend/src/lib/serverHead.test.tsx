import { act, cleanup, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { hy } from '../i18n/messages/hy'
import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'
import { resetServerHead } from './serverHead'

describe('head tags sent by the server', () => {
  beforeEach(() => {
    // What backend/seo puts in <head> for the page the visitor lands on ("/" in jsdom).
    document.head.innerHTML = `
      <title data-ssr>Server title</title>
      <meta data-ssr name="description" content="Server description" />
      <link data-ssr rel="alternate" hreflang="en" href="http://localhost/en" />
      <script data-ssr type="application/ld+json">{}</script>`
    resetServerHead()
  })

  afterEach(() => {
    cleanup() // unmount first: React removes the tags it added itself
    document.head.innerHTML = ''
    resetServerHead()
  })

  it('are kept on the first page, then replaced by the app after moving to another page', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    const { router } = renderApp('/', 'hy')
    await screen.findByRole('region', { name: /Painted for the season/ })

    // No second title, description or language links next to the server's.
    expect(document.querySelectorAll('title')).toHaveLength(1)
    expect(document.title).toBe('Server title')
    expect(document.querySelectorAll('meta[name="description"]')).toHaveLength(1)
    expect(document.querySelectorAll('link[rel="alternate"]')).toHaveLength(1)

    await act(() => router.navigate('/missing-page'))

    await waitFor(() => expect(document.title).toBe(hy.status.notFoundTitle))
    expect(document.querySelectorAll('[data-ssr]')).toHaveLength(0)
    expect(document.querySelectorAll('link[rel="alternate"]')).toHaveLength(4)
  })
})
