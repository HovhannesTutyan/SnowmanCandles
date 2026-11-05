import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { ShowcaseView } from '../../api/types'
import { setReducedMotion } from '../../test/setup'
import { ProductShowcase, type ProductShowcaseProps } from './ProductShowcase'

function view(label: string, group: ShowcaseView['group'] = 'side'): ShowcaseView {
  return {
    image: `${label}.webp`,
    label,
    short_label: label,
    caption: `${label} caption`,
    color: '#7FB045',
    tint: '#EEF3E6',
    group,
  }
}

const views = [view('Front'), view('Angle'), view('Back'), view('Top', 'top'), view('Bottom', 'bottom')]

function renderShowcase(props: Partial<ProductShowcaseProps> = {}) {
  render(<ProductShowcase title="Snowmen" price="$34.00" views={views} autoplayMs={false} {...props} />)
  const root = screen.getByRole('region', { name: 'Snowmen' })
  Object.defineProperty(root, 'clientWidth', { value: 1000, configurable: true })
  return root
}

const pressedPill = () => screen.getAllByRole('button').find((b) => b.getAttribute('aria-pressed') === 'true')?.textContent
const item = (index: number) => document.querySelector(`[data-i="${index}"]`) as HTMLElement

function drag(root: HTMLElement, from: [number, number], to: [number, number], target: Element = root) {
  fireEvent.pointerDown(target, { pointerId: 1, clientX: from[0], clientY: from[1], button: 0 })
  // In small steps, like a real drag.
  for (let step = 1; step <= 8; step++) {
    fireEvent.pointerMove(root, {
      pointerId: 1,
      clientX: from[0] + ((to[0] - from[0]) * step) / 8,
      clientY: from[1] + ((to[1] - from[1]) * step) / 8,
      pointerType: 'mouse',
    })
  }
  fireEvent.pointerUp(root, { pointerId: 1, clientX: to[0], clientY: to[1] })
}

describe('ProductShowcase', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('shows the title, price, position and the selected view text', () => {
    renderShowcase()
    expect(screen.getByText('$34.00')).toBeInTheDocument()
    expect(screen.getByText('1 / 5')).toBeInTheDocument()
    expect(screen.getByText('Front caption')).toBeInTheDocument()
    expect(pressedPill()).toBe('Front')
  })

  it('takes the colours of the selected view', () => {
    const root = renderShowcase({ views: [view('Front'), { ...view('Back'), color: '#6FA8DC', tint: '#E9F0F6' }] })
    expect(root.style.getPropertyValue('--ps-c')).toBe('#7FB045')
    fireEvent.click(screen.getByRole('button', { name: 'Back' }))
    expect(root.style.getPropertyValue('--ps-c')).toBe('#6FA8DC')
    expect(root.style.getPropertyValue('--ps-c2')).toBe('#E9F0F6')
  })

  it('moves with the pills and the arrows, wrapping around', () => {
    renderShowcase()
    fireEvent.click(screen.getByRole('button', { name: 'Back' }))
    expect(screen.getByText('3 / 5')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Next view' }))
    expect(pressedPill()).toBe('Top')
    fireEvent.click(screen.getByRole('button', { name: 'Next view' }))
    fireEvent.click(screen.getByRole('button', { name: 'Next view' }))
    expect(pressedPill()).toBe('Front')
    fireEvent.click(screen.getByRole('button', { name: 'Previous view' }))
    expect(pressedPill()).toBe('Bottom')
  })

  it('turns when dragged sideways and jumps to top/bottom when dragged down/up', () => {
    const root = renderShowcase()
    drag(root, [500, 300], [390, 300]) // left, one step (a step is 8% of the width)
    expect(pressedPill()).toBe('Angle')
    drag(root, [390, 300], [500, 300]) // right
    expect(pressedPill()).toBe('Front')
    drag(root, [500, 300], [280, 300]) // keep dragging to keep turning
    expect(pressedPill()).toBe('Back')
    fireEvent.click(screen.getByRole('button', { name: 'Front' }))
    drag(root, [500, 100], [500, 300]) // down
    expect(pressedPill()).toBe('Top')
    drag(root, [500, 300], [500, 100]) // up
    expect(pressedPill()).toBe('Bottom')
  })

  it('works from the keyboard, without Enter on a button toggling zoom', () => {
    const root = renderShowcase()
    fireEvent.keyDown(root, { key: 'ArrowRight' })
    expect(pressedPill()).toBe('Angle')
    fireEvent.keyDown(root, { key: 'ArrowUp' })
    expect(pressedPill()).toBe('Top')
    fireEvent.keyDown(root, { key: 'ArrowDown' })
    expect(pressedPill()).toBe('Bottom')

    fireEvent.keyDown(root, { key: 'Enter' })
    expect(root.className).toContain('isZoom')
    fireEvent.keyDown(root, { key: 'Escape' })
    expect(root.className).not.toContain('isZoom')

    fireEvent.keyDown(screen.getByRole('button', { name: 'Back' }), { key: 'Enter' })
    expect(root.className).not.toContain('isZoom')
  })

  it('zooms when the product is clicked, and closes on the next click', () => {
    const root = renderShowcase()
    fireEvent.pointerDown(item(0), { pointerId: 1, clientX: 500, clientY: 300, button: 0 })
    fireEvent.pointerUp(root, { pointerId: 1, clientX: 500, clientY: 300 })
    expect(root.className).toContain('isZoom')

    fireEvent.pointerDown(item(0), { pointerId: 1, clientX: 500, clientY: 300, button: 0 })
    fireEvent.pointerUp(root, { pointerId: 1, clientX: 500, clientY: 300 })
    expect(root.className).not.toContain('isZoom')
  })

  it('brings a clicked side product to the centre', () => {
    const root = renderShowcase()
    fireEvent.pointerDown(item(1), { pointerId: 1, clientX: 800, clientY: 300, button: 0 })
    fireEvent.pointerUp(root, { pointerId: 1, clientX: 800, clientY: 300 })
    expect(pressedPill()).toBe('Angle')
    expect(root.className).not.toContain('isZoom')
  })

  it('auto-plays until the visitor interacts, and pauses on hover', () => {
    const root = renderShowcase({ autoplayMs: 1000 })
    act(() => vi.advanceTimersByTime(1000))
    expect(pressedPill()).toBe('Angle')

    fireEvent.mouseEnter(root)
    act(() => vi.advanceTimersByTime(3000))
    expect(pressedPill()).toBe('Angle')
    fireEvent.mouseLeave(root)
    act(() => vi.advanceTimersByTime(1000))
    expect(pressedPill()).toBe('Back')

    fireEvent.click(screen.getByRole('button', { name: 'Front' }))
    act(() => vi.advanceTimersByTime(5000))
    expect(pressedPill()).toBe('Front')
  })

  it('does not auto-play for visitors who prefer reduced motion', () => {
    setReducedMotion(true)
    renderShowcase({ autoplayMs: 1000 })
    act(() => vi.advanceTimersByTime(5000))
    expect(pressedPill()).toBe('Front')
  })

  it('hides the controls with a single view', () => {
    renderShowcase({ views: [view('Front')] })
    expect(screen.queryByRole('button', { name: 'Next view' })).not.toBeInTheDocument()
    expect(screen.queryByText('1 / 1')).not.toBeInTheDocument()
    expect(screen.getByText('Front caption')).toBeInTheDocument()
  })
})
