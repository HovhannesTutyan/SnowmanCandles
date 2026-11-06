import { fireEvent, screen, within } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { makeCandleDetail, makeContent, makeHomeData, makeItem } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'

const ROADSTER_PATH = '/api/candles/vintage-roadster-candle/'

describe('ProductPage', () => {
  beforeEach(() => localStorage.clear())

  it('shows the product from the API', async () => {
    mockApi({ '/api/site/': makeContent(), [ROADSTER_PATH]: makeCandleDetail() })
    renderApp('/candles/vintage-roadster-candle')

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Vintage Roadster Candle' }),
    ).toBeInTheDocument()
    expect(screen.getByText('$28.00')).toBeInTheDocument()
    expect(screen.getByText('Tax included.')).toBeInTheDocument()

    const breadcrumb = screen.getByRole('navigation', { name: 'Breadcrumb' })
    expect(within(breadcrumb).getByRole('link', { name: 'Single candles' })).toBeInTheDocument()

    // Facts: product burn time and size, shared "ships in".
    expect(screen.getByText('~25 hours')).toBeInTheDocument()
    expect(screen.getByText('14 × 7 × 8 cm')).toBeInTheDocument()
    expect(screen.getByText('3–5 days')).toBeInTheDocument()

    // No making-of text of its own: the shared one is used.
    expect(screen.getByRole('heading', { name: 'Hours of small brushstrokes in every one.' })).toBeInTheDocument()

    // Related products link to their pages.
    expect(screen.getByRole('link', { name: /Carousel Candle/ })).toHaveAttribute('href', '/en/candles/carousel-candle')
  })

  it('has a gallery with main, lit and uploaded views', async () => {
    mockApi({ '/api/site/': makeContent(), [ROADSTER_PATH]: makeCandleDetail() })
    renderApp('/candles/vintage-roadster-candle')

    const views = await screen.findByRole('group', { name: 'Product views' })
    const thumbs = within(views).getAllByRole('button')
    expect(thumbs.map((t) => t.getAttribute('aria-label'))).toEqual(['Main view', 'Lit', 'Wheel detail'])

    fireEvent.click(within(views).getByRole('button', { name: 'Lit' }))
    expect(within(views).getByRole('button', { name: 'Lit' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByAltText('Vintage Roadster Candle, lit')).toBeInTheDocument()

    fireEvent.click(within(views).getByRole('button', { name: 'Wheel detail' }))
    expect(screen.getByAltText('Vintage Roadster Candle: Wheel detail')).toHaveAttribute(
      'src',
      'http://localhost/media/candles/gallery/wheel.webp',
    )
  })

  it('puts the showcase on top when the product has views', async () => {
    const views = ['Front', 'Back'].map((label) => ({
      image: `http://localhost/${label}.webp`, label, short_label: label, caption: `${label} caption`,
      color: '#7FB045', tint: '#EEF3E6', group: 'side' as const,
    }))
    mockApi({
      '/api/site/': makeContent(),
      [ROADSTER_PATH]: makeCandleDetail({ showcase_views: views, flame: null, gallery: [] }),
    })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })

    const showcase = screen.getByRole('region', { name: 'Vintage Roadster Candle' })
    expect(within(showcase).getByText('$28.00')).toBeInTheDocument()
    expect(within(showcase).getByRole('button', { name: 'Back' })).toBeInTheDocument()
    // Nothing else to show, so the regular gallery stands aside.
    expect(screen.queryByText('Hand-painted · each one unique')).not.toBeInTheDocument()
  })

  it('keeps the gallery next to the showcase for lit and extra photos', async () => {
    mockApi({
      '/api/site/': makeContent(),
      [ROADSTER_PATH]: makeCandleDetail({
        showcase_views: [{
          image: 'http://localhost/f.webp', label: 'Front', short_label: 'Front', caption: '',
          color: '#7FB045', tint: '#EEF3E6', group: 'side',
        }],
      }),
    })
    renderApp('/candles/vintage-roadster-candle')
    expect(await screen.findByRole('group', { name: 'Product views' })).toBeInTheDocument()
  })

  it('shows only the regular gallery without showcase views', async () => {
    mockApi({ '/api/site/': makeContent(), [ROADSTER_PATH]: makeCandleDetail() })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })
    expect(screen.queryByRole('region', { name: 'Vintage Roadster Candle' })).not.toBeInTheDocument()
    expect(screen.getByText('Hand-painted · each one unique')).toBeInTheDocument()
  })

  it('hides the lit view and thumbnails when there is nothing else to show', async () => {
    mockApi({
      '/api/site/': makeContent(),
      [ROADSTER_PATH]: makeCandleDetail({ flame: null, gallery: [] }),
    })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })
    expect(screen.queryByRole('group', { name: 'Product views' })).not.toBeInTheDocument()
  })

  it('adds the chosen scent and quantity to the basket', async () => {
    mockApi({ '/api/site/': makeContent(), [ROADSTER_PATH]: makeCandleDetail({ stock: 3 }) })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })

    expect(screen.getByText('Only 3 left')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Pine & cedar' }))
    expect(screen.getByRole('button', { name: 'Pine & cedar' })).toHaveAttribute('aria-pressed', 'true')

    const increase = screen.getByRole('button', { name: 'Increase quantity' })
    fireEvent.click(increase)
    fireEvent.click(increase)
    expect(increase).toBeDisabled() // capped at the stock
    expect(screen.getByLabelText('Quantity 3')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Add to basket' }))
    expect(screen.getByRole('button', { name: 'Basket, 3 items' })).toBeInTheDocument()
    expect(screen.getByText('Added to basket')).toBeInTheDocument()

    const stored = JSON.parse(localStorage.getItem('candle-shop:cart') ?? '[]')
    expect(stored).toEqual([{ key: 'candle-vintage-roadster-candle', scent: 'Pine & cedar', quantity: 3 }])
  })

  it('cannot be bought when sold out', async () => {
    mockApi({
      '/api/site/': makeContent(),
      [ROADSTER_PATH]: makeCandleDetail({ stock: 0, is_available: false }),
    })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })
    expect(screen.getByRole('button', { name: 'Sold out' })).toBeDisabled()
    expect(screen.getByText(/Sold out — back soon/)).toBeInTheDocument()
  })

  it('opens one accordion panel at a time', async () => {
    mockApi({ '/api/site/': makeContent(), [ROADSTER_PATH]: makeCandleDetail() })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })

    const details = screen.getByRole('button', { name: 'Details' })
    const care = screen.getByRole('button', { name: 'Candle care' })
    expect(details).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText('Soy wax, cotton wick.')).toBeVisible()

    fireEvent.click(care)
    expect(care).toHaveAttribute('aria-expanded', 'true')
    expect(details).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByText('Trim the wick before lighting.')).toBeVisible()
  })

  it('shows a friendly page for unknown products', async () => {
    mockApi({ '/api/site/': makeContent() }) // the detail request 404s
    renderApp('/candles/does-not-exist')
    expect(await screen.findByRole('heading', { name: "We couldn't find that piece" })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Browse the collection' })).toHaveAttribute('href', '/en#winter')
  })

  it('opens from a homepage card and moves between related products', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/home/': makeHomeData({
        featured_candles: [makeItem({ title: 'Vintage Roadster Candle', slug: 'vintage-roadster-candle' })],
      }),
      [ROADSTER_PATH]: makeCandleDetail(),
      '/api/candles/carousel-candle/': makeCandleDetail({
        title: 'Carousel Candle',
        slug: 'carousel-candle',
        related: [],
      }),
    })
    const { router } = renderApp('/')

    const grid = await screen.findByRole('region', { name: /Painted for the season/ })
    fireEvent.click(within(grid).getByRole('link', { name: 'Vintage Roadster Candle' }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Vintage Roadster Candle' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/en/candles/vintage-roadster-candle')

    fireEvent.click(screen.getByRole('link', { name: /Carousel Candle/ }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Carousel Candle' })).toBeInTheDocument()
  })

  it('shows the candles included in a collection', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/collections/winter-set/': {
        ...makeCandleDetail({
          title: 'Winter Set',
          slug: 'winter-set',
          product_type: 'collection',
          product_type_label: 'Collection',
        }),
        candle_count: 1,
        candles: [{
          title: 'Holly Bauble Candle', slug: 'holly-bauble-candle', image: 'x.webp',
          price: '24.00', tint: '#E4ECDC', product_type_label: 'Single candle', is_available: true,
        }],
      },
    })
    renderApp('/collections/winter-set')
    expect(await screen.findByRole('heading', { level: 1, name: 'Winter Set' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Holly Bauble Candle' })).toHaveAttribute(
      'href',
      '/en/candles/holly-bauble-candle',
    )
  })
})
