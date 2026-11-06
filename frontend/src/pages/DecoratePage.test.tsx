import { fireEvent, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { DecoratePageData, GalleryPicture } from '../api/types'
import { makeContent, makeHomeData } from '../test/fixtures'
import { mockApi, renderApp } from '../test/renderApp'
import { setReducedMotion } from '../test/setup'

function picture(id: number, caption: string, products: GalleryPicture['products'] = []): GalleryPicture {
  return { id, image: `http://localhost/media/decorate/gallery/${id}.webp`, caption, alt: `${caption} (alt)`, products }
}

function makeDecoratePage(overrides: Partial<DecoratePageData> = {}): DecoratePageData {
  return {
    hero_eyebrow: 'Styling & Décor',
    hero_title: 'Decorate\nwith light',
    hero_text: 'Ideas for styling candles in every room.',
    hero_link_text: 'Browse the gallery',
    hero_video: null,
    hero_image: null,
    hero_image_alt: 'A styled oak shelf',
    story_title: 'A home feels finished with candlelight',
    story_subtitle: 'A few small flames change a whole room.',
    story_text: 'Start in the **living room**, with a tray.\n\nOn the **dining table**, mix heights.',
    gallery_title: 'Gallery',
    gallery_text: 'Drag, swipe or use the arrows.',
    cta_title: 'Bring the look home',
    cta_text: 'Every candle is made by hand.',
    cta_button_text: 'Shop Candles',
    cta_image: null,
    rooms: [
      { title: 'Living room', text: 'A low tray of pillars.', gallery_index: 1 },
      { title: 'Bedroom', text: 'Keep it calm.', gallery_index: null },
    ],
    gallery: [
      picture(1, 'Roadster on a walnut table', [
        { title: 'Vintage Roadster Candle', slug: 'vintage-roadster-candle', product_type: 'candle' },
      ]),
      picture(2, 'Carousel on a linen shelf'),
      picture(3, 'Soy pillars at dusk'),
    ],
    ...overrides,
  }
}

function renderDecorate(overrides: Partial<DecoratePageData> = {}) {
  mockApi({ '/api/site/': makeContent(), '/api/decorate/': makeDecoratePage(overrides) })
  return renderApp('/decorate')
}

describe('DecoratePage', () => {
  it('shows the hero, story and rooms from the admin', async () => {
    renderDecorate()

    const heading = await screen.findByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Decorate with light')
    expect(screen.getByAltText('A styled oak shelf')).toBeInTheDocument() // design picture fallback
    expect(screen.getByRole('link', { name: 'Browse the gallery' })).toHaveAttribute('href', '#gallery')

    // **bold** in the admin text becomes <strong>.
    expect(screen.getByText('living room').tagName).toBe('STRONG')
    expect(screen.getByText('dining table').tagName).toBe('STRONG')

    const rooms = screen.getByRole('list', { name: 'Styling ideas by room' })
    expect(within(rooms).getAllByRole('listitem')).toHaveLength(2)
    // A room without a picture is shown, but isn't clickable.
    expect(within(rooms).getAllByRole('button')).toHaveLength(1)

    expect(screen.getByRole('link', { name: 'Shop Candles' })).toHaveAttribute('href', '/en#winter')
  })

  it('opens a room picture in the viewer and moves through the gallery', async () => {
    renderDecorate()
    fireEvent.click(await screen.findByRole('button', { name: /Living room: .* Open styling picture/ }))

    const viewer = screen.getByRole('dialog', { name: 'Picture viewer' })
    expect(within(viewer).getByText('2 / 3')).toBeInTheDocument()
    expect(within(viewer).getByAltText('Carousel on a linen shelf (alt)')).toBeInTheDocument()

    fireEvent.click(within(viewer).getByRole('button', { name: 'Next picture' }))
    expect(within(viewer).getByText('3 / 3')).toBeInTheDocument()
    fireEvent.keyDown(document, { key: 'ArrowRight' }) // wraps around
    expect(within(viewer).getByText('1 / 3')).toBeInTheDocument()

    // Candles in the picture link to their product pages.
    expect(within(viewer).getByRole('link', { name: 'Vintage Roadster Candle' })).toHaveAttribute(
      'href',
      '/en/candles/vintage-roadster-candle',
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('opens gallery slides full size', async () => {
    renderDecorate()
    const gallery = await screen.findByRole('region', { name: /Styling gallery, 3 pictures/ })
    fireEvent.click(within(gallery).getByRole('button', { name: 'Open picture 3 of 3: Soy pillars at dusk' }))
    const viewer = screen.getByRole('dialog')
    expect(within(viewer).getByText('Soy pillars at dusk')).toBeInTheDocument()

    fireEvent.click(within(viewer).getByRole('button', { name: 'Close picture viewer' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('hides the gallery and its link when there are no pictures', async () => {
    renderDecorate({ gallery: [], rooms: [{ title: 'Living room', text: 'A tray.', gallery_index: null }] })
    await screen.findByRole('heading', { level: 1 })
    expect(screen.queryByRole('heading', { name: 'Gallery' })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Browse the gallery' })).not.toBeInTheDocument()
  })

  it('uses uploaded hero and closing pictures', async () => {
    const { container } = renderDecorate({
      hero_image: 'http://localhost/media/decorate/hero.jpg',
      cta_image: 'http://localhost/media/decorate/cta.jpg',
    })
    await screen.findByRole('heading', { level: 1 })
    expect(screen.getByAltText('A styled oak shelf')).toHaveAttribute('src', 'http://localhost/media/decorate/hero.jpg')
    expect(container.querySelector('img[src="http://localhost/media/decorate/cta.jpg"]')).toBeInTheDocument()
  })

  it('plays the hero video, silently on a loop, instead of the picture', async () => {
    const { container } = renderDecorate({
      hero_video: 'http://localhost/media/decorate/video/hero.mp4',
      hero_image: 'http://localhost/media/decorate/poster.jpg',
    })
    await screen.findByRole('heading', { level: 1 })
    const video = container.querySelector('video') as HTMLVideoElement
    expect(video).toHaveAttribute('src', 'http://localhost/media/decorate/video/hero.mp4')
    expect(video).toHaveAttribute('poster', 'http://localhost/media/decorate/poster.jpg')
    expect(video).toHaveAttribute('aria-label', 'A styled oak shelf')
    expect(video.muted).toBe(true)
    expect(video.loop).toBe(true)
    expect(video.autoplay).toBe(true)
    expect(screen.queryByAltText('A styled oak shelf')).not.toBeInTheDocument()
  })

  it('does not autoplay the hero video for visitors who prefer reduced motion', async () => {
    setReducedMotion(true)
    const { container } = renderDecorate({ hero_video: 'http://localhost/media/decorate/video/hero.mp4' })
    await screen.findByRole('heading', { level: 1 })
    const video = container.querySelector('video') as HTMLVideoElement
    expect(video.autoplay).toBe(false)
    expect(video.controls).toBe(true)
  })

  it('is linked from the header, the footer and the homepage', async () => {
    mockApi({
      '/api/site/': makeContent(),
      '/api/home/': makeHomeData(),
      '/api/decorate/': makeDecoratePage(),
    })
    const { router } = renderApp('/')
    await screen.findByRole('heading', { level: 1 })

    const footer = screen.getByRole('contentinfo')
    expect(within(footer).getByRole('link', { name: 'Decorate with candles' })).toHaveAttribute('href', '/en/decorate')
    const shopByType = screen.getByRole('region', { name: 'Shop by type' })
    expect(within(shopByType).getByRole('link', { name: /decorate with candles/ })).toHaveAttribute('href', '/en/decorate')

    fireEvent.click(within(screen.getByRole('banner')).getByRole('link', { name: 'Inspiration' }))
    expect(await screen.findByRole('heading', { level: 1, name: /Decorate/ })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/en/decorate')
    expect(within(screen.getByRole('banner')).getByRole('link', { name: 'Inspiration' })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })
})
