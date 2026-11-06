import { fireEvent, screen, within } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'

describe('HomePage', () => {
  beforeEach(() => localStorage.clear())

  it('renders the site content and featured products from the API', async () => {
    const fetchSpy = mockApi({
      '/api/site/': makeContent({ studio_name: 'Glow Studio', contact_email: 'hi@glow.test' }),
      '/api/home/': makeHomeData(),
    })
    renderApp('/')

    expect(screen.getByRole('status')).toBeInTheDocument() // loading
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Little candles for the longest nights.' }),
    ).toBeInTheDocument()
    expect(fetchSpy).toHaveBeenCalledTimes(2) // site + home

    // Brand and contact details come from Site content.
    expect(screen.getByRole('banner')).toHaveTextContent('Glow Studio')
    expect(screen.getByRole('link', { name: 'hi@glow.test' })).toHaveAttribute('href', 'mailto:hi@glow.test')

    // Featured candles and collections share the grid, with formatted prices.
    const grid = screen.getByRole('region', { name: /Painted for the season/ })
    expect(within(grid).getAllByRole('article')).toHaveLength(2)
    expect(within(grid).getByText('$24.00')).toBeInTheDocument()

    // Uploaded section image is used.
    expect(screen.getByAltText('The same piece after hand-painting')).toHaveAttribute(
      'src',
      'http://localhost/media/homepage/after.webp',
    )
  })

  it('links products to their pages', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/')

    const grid = await screen.findByRole('region', { name: /Painted for the season/ })
    expect(within(grid).getByRole('link', { name: 'Holly Bauble Candle' })).toHaveAttribute(
      'href',
      '/en/candles/holly-bauble-candle',
    )
    expect(within(grid).getByRole('link', { name: 'Winter Set' })).toHaveAttribute(
      'href',
      '/en/collections/winter-set',
    )
    // The hero caption links to the slide's product.
    expect(screen.getByRole('link', { name: 'Snowmen by the Campfire' })).toHaveAttribute(
      'href',
      '/en/candles/snowmen',
    )
  })

  it('counts "Add to basket" in the header badge', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/')

    const grid = await screen.findByRole('region', { name: /Painted for the season/ })
    fireEvent.click(within(grid).getByRole('button', { name: 'Add to basket: Holly Bauble Candle' }))
    expect(screen.getByRole('button', { name: 'Basket, 1 item' })).toBeInTheDocument()
    expect(within(grid).getByRole('button', { name: /Added ✓/ })).toBeInTheDocument()
  })

  it('offers exactly two types: single candles and candle sets', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/')
    const section = await screen.findByRole('region', { name: 'Shop by type' })
    const tiles = within(section).getAllByRole('link').filter((link) => link.getAttribute('href') === '#winter')
    expect(tiles.map((tile) => tile.querySelector('div > div')?.textContent)).toEqual([
      'Single candles',
      'Candle sets',
    ])
    expect(within(section).getByRole('link', { name: /decorate with candles/ })).toHaveAttribute('href', '/en/decorate')
  })

  it('shows an empty state when nothing is featured', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/home/': makeHomeData({ featured_candles: [], featured_collections: [] }),
    })
    renderApp('/')
    expect(await screen.findByText(/New pieces are on their way/)).toBeInTheDocument()
  })

  it('shows an error with a retry button when the API fails', async () => {
    const spy = mockApi({ '/api/site/': 500 })
    renderApp('/')
    expect(await screen.findByRole('alert')).toHaveTextContent("The shop couldn't load")

    spy.mockRestore()
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  it('opens and closes the mobile menu', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/')
    const button = await screen.findByRole('button', { name: 'Open menu' })

    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.getByRole('button', { name: 'Open menu' })).toHaveAttribute('aria-expanded', 'false')
  })
})
