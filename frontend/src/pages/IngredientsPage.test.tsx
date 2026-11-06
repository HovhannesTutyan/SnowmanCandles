import { fireEvent, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { IngredientChapter, IngredientsPageData } from '../api/types'
import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'

function makeChapter(overrides: Partial<IngredientChapter> = {}): IngredientChapter {
  return {
    anchor: 'soy',
    nav_label: 'Soy Wax',
    title: 'Soy wax',
    intro: 'The fuel of every candle we pour.',
    paragraphs: ['Soy wax starts as oil pressed from soybeans.', 'We use soy wax.'],
    illustration: 'soy',
    banner_image: null,
    banner_color: '#EFE3CC',
    banner_text: 'dark',
    cards_title: '',
    points: [{ lead: 'Renewable', text: 'made from a crop replanted every year.' }],
    questions: [
      { question: 'From soybean to candle', answer: 'Pressed, refined and poured.' },
      { question: 'Soy vs. paraffin', answer: 'Paraffin comes from petroleum.' },
    ],
    cards: [],
    swatches: [],
    ...overrides,
  }
}

function makeIngredientsPage(overrides: Partial<IngredientsPageData> = {}): IngredientsPageData {
  return {
    nav_title: 'Ingredients',
    hero_eyebrow: 'Ingredients',
    hero_title: "What's inside our candles",
    hero_text: 'Five honest things.',
    hero_link_text: 'Start with the wax',
    hero_image: null,
    hero_image_label: 'Raw plaster, before painting',
    cta_title: 'Made by hand, made to last',
    cta_text: 'Soy to burn, plaster to keep.',
    cta_button_text: 'Shop Candles',
    chapters: [
      makeChapter(),
      makeChapter({
        anchor: 'wick',
        nav_label: 'Wick',
        title: 'Wick',
        illustration: 'wick',
        banner_text: 'light',
        questions: [],
        points: [],
        cards_title: 'About our wicks',
        cards: [{ icon: 'braid', title: 'Braided cotton', text: 'A soft, steady flame.' }],
      }),
      makeChapter({
        anchor: 'colour',
        nav_label: 'Colour',
        title: 'Colour',
        illustration: 'colour',
        questions: [],
        points: [],
        swatches: [
          { name: 'Sage', color: '#A9B39A', note: 'Fresh & herbal' },
          { name: 'Pine', color: '#3E5A4A', note: '' },
        ],
      }),
    ],
    ...overrides,
  }
}

describe('IngredientsPage', () => {
  it('shows the hero, chapters and closing call to action from the admin', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/ingredients/': makeIngredientsPage() })
    renderApp('/ingredients')

    expect(await screen.findByRole('heading', { level: 1, name: "What's inside our candles" })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Start with the wax' })).toHaveAttribute('href', '#soy')
    expect(screen.getByText('Raw plaster, before painting')).toBeInTheDocument()

    const soy = screen.getByRole('region', { name: 'Soy wax' })
    expect(within(soy).getByText('Soy wax starts as oil pressed from soybeans.')).toBeInTheDocument()
    expect(within(soy).getByText('Renewable')).toBeInTheDocument()

    const wick = screen.getByRole('region', { name: 'Wick' })
    expect(within(wick).getByRole('heading', { name: 'About our wicks' })).toBeInTheDocument()
    expect(within(wick).getByText('Braided cotton')).toBeInTheDocument()

    const colour = screen.getByRole('region', { name: 'Colour' })
    expect(within(colour).getByRole('list', { name: 'Colour palette' })).toBeInTheDocument()
    expect(within(colour).getByText('Fresh & herbal')).toBeInTheDocument()

    expect(screen.getByRole('link', { name: 'Shop Candles' })).toHaveAttribute('href', '/en#winter')
  })

  it('opens questions independently, with the first one open', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/ingredients/': makeIngredientsPage() })
    renderApp('/ingredients')

    const first = await screen.findByRole('button', { name: 'From soybean to candle' })
    const second = screen.getByRole('button', { name: 'Soy vs. paraffin' })
    expect(first).toHaveAttribute('aria-expanded', 'true')
    expect(second).toHaveAttribute('aria-expanded', 'false')

    fireEvent.click(second)
    expect(second).toHaveAttribute('aria-expanded', 'true')
    expect(first).toHaveAttribute('aria-expanded', 'true') // both can be open
    expect(screen.getByText('Paraffin comes from petroleum.')).toBeVisible()
  })

  it('lists every chapter in the bottom bar', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/ingredients/': makeIngredientsPage() })
    renderApp('/ingredients')
    const nav = await screen.findByRole('navigation', { name: 'Ingredients on this page' })
    expect(within(nav).getAllByRole('link').map((a) => a.textContent)).toEqual([
      'Ingredients',
      'Soy Wax',
      'Wick',
      'Colour',
    ])
  })

  it('uses uploaded photos instead of the drawn pictures', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/ingredients/': makeIngredientsPage({
        hero_image: 'http://localhost/media/ingredients/hero.jpg',
        chapters: [makeChapter({ banner_image: 'http://localhost/media/ingredients/soy.jpg' })],
      }),
    })
    const { container } = renderApp('/ingredients')
    await screen.findByRole('heading', { level: 1 })
    expect(container.querySelector('img[src="http://localhost/media/ingredients/hero.jpg"]')).toBeInTheDocument()
    expect(container.querySelector('img[src="http://localhost/media/ingredients/soy.jpg"]')).toBeInTheDocument()
    expect(screen.queryByRole('img', { name: /unpainted plaster vessel/ })).not.toBeInTheDocument()
  })

  it('is linked from the header and footer', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/home/': makeHomeData(),
      '/api/ingredients/': makeIngredientsPage(),
    })
    const { router } = renderApp('/')
    await screen.findByRole('heading', { level: 1 })

    const header = screen.getByRole('banner')
    expect(within(header).getByRole('link', { name: 'Candle care' })).toHaveAttribute('href', '/en/candle-care')
    const footer = screen.getByRole('contentinfo')
    expect(within(footer).getByRole('link', { name: "What's inside our candles" })).toHaveAttribute('href', '/en/ingredients')

    fireEvent.click(within(header).getByRole('link', { name: 'Ingredients' }))
    expect(await screen.findByRole('heading', { level: 1, name: "What's inside our candles" })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/en/ingredients')
    expect(within(screen.getByRole('banner')).getByRole('link', { name: 'Ingredients' })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })
})
