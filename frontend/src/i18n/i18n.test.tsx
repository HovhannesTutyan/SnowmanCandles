import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'
import { localizePath, splitLocale } from './locales'
import { en } from './messages/en'
import { hy } from './messages/hy'
import { ru } from './messages/ru'

describe('language paths', () => {
  it('adds the prefix for English and Russian, none for Armenian', () => {
    expect(localizePath('/candle-care', 'hy')).toBe('/candle-care')
    expect(localizePath('/candle-care', 'en')).toBe('/en/candle-care')
    expect(localizePath('/', 'ru')).toBe('/ru')
    expect(localizePath('/#winter', 'ru')).toBe('/ru#winter')
    expect(localizePath('#footer', 'en')).toBe('#footer')
  })

  it('reads the language from a pathname', () => {
    expect(splitLocale('/ru/candles/x')).toEqual({ locale: 'ru', path: '/candles/x' })
    expect(splitLocale('/en')).toEqual({ locale: 'en', path: '/' })
    expect(splitLocale('/candle-care')).toEqual({ locale: 'hy', path: '/candle-care' })
    expect(splitLocale('/english-tea')).toEqual({ locale: 'hy', path: '/english-tea' })
  })
})

describe('language files', () => {
  it('have the same texts as English', () => {
    const keys = (messages: object): string[] =>
      Object.entries(messages).flatMap(([key, value]) =>
        value && typeof value === 'object' && !Array.isArray(value)
          ? keys(value).map((k) => `${key}.${k}`)
          : [key],
      )
    expect(keys(hy)).toEqual(keys(en))
    expect(keys(ru)).toEqual(keys(en))
  })

  it('use Russian plural forms', () => {
    expect(ru.header.cart(1)).toBe('Корзина, 1 товар')
    expect(ru.header.cart(3)).toBe('Корзина, 3 товара')
    expect(ru.header.cart(11)).toBe('Корзина, 11 товаров')
    expect(ru.header.cart(22)).toBe('Корзина, 22 товара')
  })
})

describe('the site in each language', () => {
  beforeEach(() => localStorage.clear())

  it('opens in Armenian at the site root and asks the API for Armenian texts', async () => {
    const fetchSpy = mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/', 'hy')

    await screen.findByRole('heading', { level: 1 }) // the homepage has loaded
    const header = screen.getByRole('banner')
    expect(within(header).getByRole('link', { name: hy.nav.care })).toHaveAttribute('href', '/candle-care')
    await waitFor(() => expect(document.documentElement.lang).toBe('hy-AM'))
    const urls = fetchSpy.mock.calls.map(([input]) => String(input))
    expect(urls).toContain('/api/site/?lang=hy')
    expect(urls).toContain('/api/home/?lang=hy')
  })

  it('keeps links in Russian under /ru', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/', 'ru')

    const header = await screen.findByRole('banner')
    expect(within(header).getByRole('link', { name: ru.nav.care })).toHaveAttribute('href', '/ru/candle-care')
    await waitFor(() => expect(document.documentElement.lang).toBe('ru-RU'))
  })

  it('switches language from the header menu, staying on the same page', async () => {
    const fetchSpy = mockApi({ '/api/site/': makeContent(), '/api/care/': 404 })
    const { router } = renderApp('/candle-care?x=1', 'en')

    const button = await screen.findByRole('button', { name: 'Language: English' })
    expect(button).toHaveAttribute('aria-expanded', 'false')
    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')

    const russian = screen.getByRole('link', { name: 'Русский' })
    expect(russian).toHaveAttribute('href', '/ru/candle-care?x=1')
    expect(screen.getByRole('link', { name: 'Հայերեն' })).toHaveAttribute('href', '/candle-care?x=1')
    expect(screen.getByRole('link', { name: 'English' })).toHaveAttribute('aria-current', 'true')

    fireEvent.click(russian)
    expect(router.state.location.pathname).toBe('/ru/candle-care')
    expect(await screen.findByRole('button', { name: 'Язык: Русский' })).toBeInTheDocument()
    await waitFor(() =>
      expect(fetchSpy.mock.calls.map(([input]) => String(input))).toContain('/api/site/?lang=ru'),
    )
  })

  it('closes the language menu with Escape', async () => {
    mockApi({ '/api/site/': makeContent(), '/api/home/': makeHomeData() })
    renderApp('/')
    const button = await screen.findByRole('button', { name: 'Language: English' })
    fireEvent.click(button)
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(button).toHaveFocus()
  })
})
