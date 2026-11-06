import { act, fireEvent, render as rtlRender, screen } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createPriceFormatter } from '../../lib/format'
import { makeSlide } from '../../test/fixtures'
import { setReducedMotion } from '../../test/setup'
import { HeroShowcase, SLIDE_DURATION_MS } from './HeroShowcase'

const slides = [
  makeSlide({ id: 1, title: 'Snowmen' }),
  makeSlide({ id: 2, title: 'Roadster', link: { type: 'candle', slug: 'roadster', price: '28.00', product_type: 'candle', product_type_label: 'Single candle' } }),
  makeSlide({ id: 3, title: 'Carousel', subtitle: 'Limited edition', link: null }),
]

const formatPrice = createPriceFormatter('USD')

// Captions link to product pages, so the showcase needs a router.
const render = (ui: ReactElement) => rtlRender(<MemoryRouter>{ui}</MemoryRouter>)

function currentTitle() {
  return screen.getByRole('button', { current: true }).getAttribute('aria-label')
}

describe('HeroShowcase', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('shows the linked item type and price, or the subtitle', () => {
    render(<HeroShowcase slides={slides} formatPrice={formatPrice} fallbackImage="x.webp" />)
    expect(screen.getByText('Candle set · $34.00')).toBeInTheDocument()
    expect(screen.getByText('Single candle · $28.00')).toBeInTheDocument()
    expect(screen.getByText('Limited edition')).toBeInTheDocument()
  })

  it('advances automatically and loops', () => {
    render(<HeroShowcase slides={slides} formatPrice={formatPrice} fallbackImage="x.webp" />)
    expect(currentTitle()).toBe('Show Snowmen')

    act(() => vi.advanceTimersByTime(SLIDE_DURATION_MS))
    expect(currentTitle()).toBe('Show Roadster')

    act(() => vi.advanceTimersByTime(SLIDE_DURATION_MS))
    expect(currentTitle()).toBe('Show Carousel')

    act(() => vi.advanceTimersByTime(SLIDE_DURATION_MS))
    expect(currentTitle()).toBe('Show Snowmen')
  })

  it('jumps to a slide when its bar is clicked and pauses on hover', () => {
    const { container } = render(
      <HeroShowcase slides={slides} formatPrice={formatPrice} fallbackImage="x.webp" />,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Show Carousel' }))
    expect(currentTitle()).toBe('Show Carousel')

    fireEvent.mouseEnter(container.querySelector('div')!)
    act(() => vi.advanceTimersByTime(SLIDE_DURATION_MS * 3))
    expect(currentTitle()).toBe('Show Carousel')
  })

  it('does not auto-advance when reduced motion is preferred', () => {
    setReducedMotion(true)
    render(<HeroShowcase slides={slides} formatPrice={formatPrice} fallbackImage="x.webp" />)
    act(() => vi.advanceTimersByTime(SLIDE_DURATION_MS * 3))
    expect(currentTitle()).toBe('Show Snowmen')
  })

  it('shows the fallback piece when there are no slides', () => {
    const { container } = render(
      <HeroShowcase slides={[]} formatPrice={formatPrice} fallbackImage="fallback.webp" />,
    )
    expect(container.querySelector('img[src="fallback.webp"]')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
