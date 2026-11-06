import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import type { CartQuoteLine } from '../api/types'
import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'

const HOLLY: CartQuoteLine = {
  kind: 'candle',
  slug: 'holly-bauble-candle',
  title: 'Holly Bauble Candle',
  image: 'http://localhost/media/holly.webp',
  tint: '#E4ECDC',
  product_type: 'candle',
  price: '24.00',
  scent: 'Pine & cedar',
  stock: 5,
}
const ROADSTER: CartQuoteLine = { ...HOLLY, slug: 'vintage-roadster-candle', title: 'Vintage Roadster Candle', price: '28.00', scent: '', stock: 2 }

function storeCart(lines: { key: string; scent: string | null; quantity: number }[]) {
  localStorage.setItem('candle-shop:cart', JSON.stringify(lines))
}

const storedCart = () => JSON.parse(localStorage.getItem('candle-shop:cart') ?? '[]')

describe('Basket', () => {
  beforeEach(() => localStorage.clear())

  it('opens the basket panel after adding a product, with prices from the API', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/home/': makeHomeData(),
      '/api/cart/': { lines: [HOLLY] },
    })
    renderApp('/')
    const grid = await screen.findByRole('region', { name: /Painted for the season/ })
    fireEvent.click(within(grid).getByRole('button', { name: 'Add to basket: Holly Bauble Candle' }))

    const panel = await screen.findByRole('dialog', { name: /Your basket/ })
    expect(await within(panel).findByRole('link', { name: 'Holly Bauble Candle' })).toHaveAttribute(
      'href',
      '/en/candles/holly-bauble-candle',
    )
    expect(within(panel).getAllByText('$24.00').length).toBeGreaterThan(0)
    expect(within(panel).getByText('Free')).toBeInTheDocument()
    expect(within(panel).getByRole('link', { name: 'View basket' })).toHaveAttribute('href', '/en/basket')
    expect(within(panel).getByRole('link', { name: 'Checkout' })).toHaveAttribute('href', '/en/checkout')

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    // The bag icon opens it again.
    fireEvent.click(screen.getByRole('button', { name: 'Basket, 1 item' }))
    expect(screen.getByRole('dialog', { name: /Your basket/ })).toBeInTheDocument()
  })

  it('changes quantities, removes lines and shows the totals on the basket page', async () => {
    storeCart([
      { key: 'candle-holly-bauble-candle', scent: 'Pine & cedar', quantity: 1 },
      { key: 'candle-vintage-roadster-candle', scent: null, quantity: 1 },
    ])
    mockApi({ '/api/site/': makeContent(), '/api/cart/': { lines: [HOLLY, ROADSTER] } })
    renderApp('/basket')

    expect(await screen.findByRole('heading', { level: 1, name: 'Your basket' })).toBeInTheDocument()
    await screen.findByRole('link', { name: 'Vintage Roadster Candle' })
    expect(screen.getAllByText('$52.00')).toHaveLength(2) // subtotal and total

    const holly = screen.getByRole('group', { name: 'Quantity of Holly Bauble Candle' })
    fireEvent.click(within(holly).getByRole('button', { name: 'Increase quantity' }))
    expect(within(holly).getByText('2')).toBeInTheDocument()
    expect(screen.getAllByText('$76.00')).toHaveLength(2)
    expect(storedCart()[0].quantity).toBe(2)

    fireEvent.click(screen.getByRole('button', { name: 'Remove Vintage Roadster Candle from the basket' }))
    expect(screen.queryByRole('link', { name: 'Vintage Roadster Candle' })).not.toBeInTheDocument()
    expect(screen.getAllByText('$48.00').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: /Proceed to checkout/ })).toHaveAttribute('href', '/en/checkout')
  })

  it('stops at the stock and blocks checkout when there are too few left', async () => {
    storeCart([{ key: 'candle-vintage-roadster-candle', scent: null, quantity: 3 }])
    mockApi({ '/api/site/': makeContent(), '/api/cart/': { lines: [ROADSTER] } })
    renderApp('/basket')

    expect(await screen.findByText('Only 2 left. Please lower the quantity.')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Proceed to checkout/ })).not.toBeInTheDocument()
    const group = screen.getByRole('group', { name: 'Quantity of Vintage Roadster Candle' })
    expect(within(group).getByRole('button', { name: 'Increase quantity' })).toBeDisabled()
    fireEvent.click(within(group).getByRole('button', { name: 'Decrease quantity' }))
    expect(screen.queryByText(/Only 2 left/)).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Proceed to checkout/ })).toBeInTheDocument()
  })

  it('marks products that are no longer sold', async () => {
    storeCart([{ key: 'candle-gone', scent: null, quantity: 1 }])
    mockApi({ '/api/site/': makeContent(), '/api/cart/': { lines: [null] } })
    renderApp('/basket')
    expect(await screen.findByText('No longer available. Please remove it.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /Remove/ }))
    expect(screen.getByText('Your basket is empty.')).toBeInTheDocument()
  })

  it('shows "Try again" instead of crashing when the basket answer is empty', async () => {
    storeCart([{ key: 'candle-holly-bauble-candle', scent: null, quantity: 1 }])
    mockApi({ '/api/site/': makeContent(), '/api/cart/': null })
    renderApp('/basket')
    expect(await screen.findByText("We couldn't load your basket.")).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1, name: 'Your basket' })).toBeInTheDocument()
  })

  it('shows an empty basket', async () => {
    mockApi({ '/api/site/': makeContent() })
    renderApp('/basket')
    expect(await screen.findByText('Your basket is empty.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Continue shopping' })).toHaveAttribute('href', '/en#winter')
  })
})

describe('Checkout', () => {
  beforeEach(() => {
    localStorage.clear()
    storeCart([{ key: 'candle-holly-bauble-candle', scent: 'Pine & cedar', quantity: 2 }])
  })

  const fill = (label: RegExp, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } })

  it('checks the required fields before sending', async () => {
    const fetchSpy = mockApi({ '/api/site/': makeContent(), '/api/cart/': { lines: [HOLLY] } })
    renderApp('/checkout')
    await screen.findByRole('heading', { level: 1, name: 'Checkout' })
    await screen.findByText('Holly Bauble Candle')
    fill(/^Phone/, 'abc')
    fireEvent.click(screen.getByRole('button', { name: 'Place order' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Please check the highlighted fields.')
    expect(screen.getByLabelText(/^Full name/)).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('Please enter a valid phone number.')).toBeInTheDocument()
    expect(screen.getByLabelText(/^Email/)).not.toHaveAttribute('aria-invalid') // optional
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes('/api/orders/'))).toBe(false)
  })

  it('places the order, clears the basket and says thank you', async () => {
    const fetchSpy = mockApi({
      '/api/site/': makeContent(),
      '/api/cart/': { lines: [HOLLY] },
      '/api/orders/': { number: 'CC-00042', total: '48.00' },
    })
    renderApp('/checkout')
    await screen.findByText('Holly Bauble Candle')
    expect(screen.getAllByText('$48.00').length).toBeGreaterThan(0)

    fill(/^Full name/, 'Anna Petrosyan')
    fill(/^Phone/, '+374 91 234567')
    fill(/^City/, 'Yerevan')
    fill(/^Street address/, 'Abovyan 10')
    fireEvent.click(screen.getByRole('button', { name: 'Place order' }))

    expect(await screen.findByRole('heading', { name: 'Thank you for your order!' })).toBeInTheDocument()
    expect(screen.getByText('Order number: CC-00042')).toBeInTheDocument()
    expect(screen.getByText('Thank you! We will call you soon.')).toBeInTheDocument()
    await waitFor(() => expect(storedCart()).toEqual([]))

    const call = fetchSpy.mock.calls.find(([url]) => String(url).includes('/api/orders/'))!
    expect(String(call[0])).toBe('/api/orders/?lang=en')
    expect(JSON.parse(String(call[1]!.body))).toEqual({
      items: [{ kind: 'candle', slug: 'holly-bauble-candle', scent: 'Pine & cedar', quantity: 2 }],
      full_name: 'Anna Petrosyan',
      phone: '+374 91 234567',
      email: '',
      city: 'Yerevan',
      address: 'Abovyan 10',
      notes: '',
      language: 'en',
      website: '',
    })
  })

  it('explains when stock ran out while ordering', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/cart/': { lines: [HOLLY] }, '/api/orders/': 409 })
    renderApp('/checkout')
    await screen.findByText('Holly Bauble Candle')
    fill(/^Full name/, 'Anna')
    fill(/^Phone/, '091234567')
    fill(/^City/, 'Yerevan')
    fill(/^Street address/, 'Abovyan 10')
    fireEvent.click(screen.getByRole('button', { name: 'Place order' }))
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(/just sold out or run low/))
    expect(storedCart()).toHaveLength(1)
  })

  it('sends people with an empty basket back to the shop', async () => {
    localStorage.clear()
    mockApi({ '/api/site/': makeContent() })
    renderApp('/checkout')
    expect(await screen.findByText('Your basket is empty')).toBeInTheDocument()
  })
})
