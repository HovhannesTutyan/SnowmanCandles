import { fireEvent, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { CarePageData } from '../api/types'
import { makeCandleDetail, makeContent, makeHomeData, makeItem } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'

function makeCarePage(overrides: Partial<CarePageData> = {}): CarePageData {
  return {
    hero_title: 'The art of a\nperfect burn',
    hero_text: 'Every piece we make is cast and painted by hand.',
    hero_image: null,
    tips_eyebrow: 'Four habits for a better burn',
    tips: [
      { title: 'Let the first burn go wide', text: 'Wax remembers.' },
      { title: 'Trim before every light', text: 'About 5 mm.' },
    ],
    rituals_title: 'Little rituals that keep your candles beautiful',
    rituals: [{ title: 'Store them cool and dark', text: 'A cupboard is perfect.' }],
    fragrance_eyebrow: 'Fragrance & afterlife',
    fragrance_title: 'Make every hour of scent count',
    fragrance_text: 'Fragrance lives in the melt pool.',
    fragrance_image: null,
    fragrance_tips: [{ lead: 'Give it time to bloom.', text: 'Usually 1 to 2 hours in.' }],
    fragrance_product: makeItem({ title: 'Holly Bauble Candle', slug: 'holly-bauble-candle', price: '24.00' }),
    faq_title: 'F.A.Q.',
    faqs: [
      { question: 'How long should I burn my candle?', answer: 'Until the pool reaches the edge.' },
      { question: 'Why is my candle smoking?', answer: 'Usually the wick is too long.' },
    ],
    ...overrides,
  }
}

describe('CareTipsPage', () => {
  it('shows the care page content from the admin', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/care/': makeCarePage() })
    renderApp('/candle-care')

    const heading = await screen.findByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('The art of a perfect burn')
    // The illustrated scene stands in until a photo is uploaded.
    expect(
      screen.getByRole('img', { name: /Painted candles glowing on a wooden table/ }),
    ).toBeInTheDocument()

    const tips = screen.getByRole('region', { name: 'Four habits for a better burn' })
    expect(within(tips).getAllByRole('listitem')).toHaveLength(2)
    expect(within(tips).getByText('02')).toBeInTheDocument()

    expect(screen.getByText('Store them cool and dark')).toBeInTheDocument()
    expect(screen.getByText('Give it time to bloom.')).toBeInTheDocument()

    // The featured candle label links to its product page, with its price.
    expect(screen.getByRole('link', { name: 'Holly Bauble Candle · $24.00' })).toHaveAttribute(
      'href',
      '/en/candles/holly-bauble-candle',
    )
  })

  it('uses uploaded photos instead of the illustrated scenes', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/care/': makeCarePage({
        hero_image: 'http://localhost/media/care/hero.jpg',
        fragrance_image: 'http://localhost/media/care/shelf.jpg',
        fragrance_product: null,
      }),
    })
    renderApp('/candle-care')
    await screen.findByRole('heading', { level: 1 })

    expect(screen.getByAltText(/glowing on a wooden table/)).toHaveAttribute('src', 'http://localhost/media/care/hero.jpg')
    expect(screen.getByAltText(/on a warm wooden shelf/)).toHaveAttribute('src', 'http://localhost/media/care/shelf.jpg')
    expect(screen.queryByRole('link', { name: /·/ })).not.toBeInTheDocument()
  })

  it('opens one FAQ answer at a time', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/care/': makeCarePage() })
    renderApp('/candle-care')

    const first = await screen.findByRole('button', { name: 'How long should I burn my candle?' })
    const second = screen.getByRole('button', { name: 'Why is my candle smoking?' })
    expect(first).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText('Until the pool reaches the edge.')).toBeVisible()

    fireEvent.click(second)
    expect(second).toHaveAttribute('aria-expanded', 'true')
    expect(first).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByText('Usually the wick is too long.')).toBeVisible()

    fireEvent.click(second)
    expect(second).toHaveAttribute('aria-expanded', 'false')
  })

  it('has a section bar that skips empty sections', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/care/': makeCarePage({ rituals: [] }) })
    renderApp('/candle-care')
    const nav = await screen.findByRole('navigation', { name: 'On this page' })
    const links = within(nav).getAllByRole('link').map((link) => link.getAttribute('href'))
    expect(links).toEqual(['#top', '#tips', '#fragrance', '#faq'])
  })

  it('is linked from the header, footer and the homepage', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData(), '/api/care/': makeCarePage() })
    const { router } = renderApp('/')
    await screen.findByRole('heading', { level: 1 })

    const header = screen.getByRole('banner')
    expect(within(header).getByRole('link', { name: 'Candle care' })).toHaveAttribute('href', '/en/candle-care')
    const footer = screen.getByRole('contentinfo')
    expect(within(footer).getByRole('link', { name: 'Candle care & tips' })).toHaveAttribute('href', '/en/candle-care')

    const howItsMade = screen.getByRole('region', { name: 'Every piece starts out white.' })
    fireEvent.click(within(howItsMade).getByRole('link', { name: 'Candle care & tips' }))
    expect(await screen.findByRole('heading', { level: 1, name: /perfect burn/ })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/en/candle-care')
    expect(within(screen.getByRole('banner')).getByRole('link', { name: 'Candle care' })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })

  it('is linked from the product page care panel', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/candles/vintage-roadster-candle/': makeCandleDetail() })
    renderApp('/candles/vintage-roadster-candle')
    await screen.findByRole('heading', { level: 1 })
    fireEvent.click(screen.getByRole('button', { name: 'Candle care' }))
    expect(screen.getByRole('link', { name: 'Read the full care guide' })).toHaveAttribute('href', '/en/candle-care')
  })
})
