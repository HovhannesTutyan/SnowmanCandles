import type { CandleDetail, HeroSlide, HomeData, ShopItem, SiteContent } from '../api/types'

export function makeItem(overrides: Partial<ShopItem> = {}): ShopItem {
  return {
    id: 1,
    title: 'Holly Bauble Candle',
    slug: 'holly-bauble-candle',
    description: 'A bauble candle with hand-painted holly.',
    image: 'http://localhost/media/candles/holly.webp',
    price: '24.00',
    stock: 10,
    tint: '#E4ECDC',
    is_available: true,
    is_featured: true,
    product_type: 'candle',
    product_type_label: 'Single candle',
    created_at: '2026-11-02T10:00:00Z',
    updated_at: '2026-11-02T10:00:00Z',
    ...overrides,
  }
}

export function makeSlide(overrides: Partial<HeroSlide> = {}): HeroSlide {
  return {
    id: 1,
    title: 'Snowmen by the Campfire',
    subtitle: '',
    image: 'http://localhost/media/candles/snowmen.webp',
    button_text: '',
    link: { type: 'candle', slug: 'snowmen', price: '34.00', product_type_label: 'Candle set' },
    ...overrides,
  }
}

export function makeContent(overrides: Partial<SiteContent> = {}): SiteContent {
  return {
    studio_name: 'Celeb Candles',
    accent_color: '#B4451A',
    currency: 'USD',
    ticker_messages: ['Winter collection is here', 'Every piece hand-painted'],
    hero_eyebrow: 'Hand-cast · Hand-painted · Small batches',
    hero_title: 'Little candles for the longest nights.',
    hero_text: 'Single candles and candle sets.',
    hero_button_text: 'Shop the winter collection',
    hero_video_button_text: "Watch how it's made",
    collection_eyebrow: 'The winter collection',
    collection_title: 'Painted for the season, made to stay out all year.',
    made_title: 'Every piece starts out white.',
    made_text: 'Watch a plain plaster bauble become a painted candle.',
    step1_title: 'Cast',
    step1_text: 'Plaster is poured into the mould.',
    step2_title: 'Paint',
    step2_text: 'Each leaf is painted with a fine brush.',
    step3_title: 'Finish & pour',
    step3_text: 'Sealed and filled with wax.',
    video_title: 'A day in the studio',
    video_caption: 'Studio video',
    video_url: '',
    single_tile_text: 'One hand-painted piece',
    sets_tile_text: 'Little winter scenes',
    custom_title: 'Want it in your colours?',
    custom_text: 'Pick a piece and tell us your palette.',
    custom_button_text: 'Request a custom piece',
    newsletter_title: 'Be first to see new pieces',
    newsletter_text: 'New designs come in small batches.',
    footer_text: 'Hand-cast, hand-painted candles and candle sets.',
    contact_email: '',
    contact_phone: '',
    instagram_handle: '',
    price_note: 'Tax included.',
    ships_in: '3–5 days',
    care_text: 'Trim the wick before lighting.',
    shipping_text: 'Wrapped by hand and sent with tracking.',
    story_title: 'Hours of small brushstrokes in every one.',
    story_text: 'Each piece is cast, painted and poured by hand.',
    images: {
      made_before: null,
      made_after: 'http://localhost/media/homepage/after.webp',
      video: null,
      single_tile: null,
      sets_tile: null,
      custom_1: null,
      custom_2: null,
    },
    ...overrides,
  }
}

export function makeHomeData(overrides: Partial<HomeData> = {}): HomeData {
  return {
    slides: [makeSlide()],
    featured_candles: [makeItem()],
    featured_collections: [
      {
        ...makeItem({
          id: 1,
          title: 'Winter Set',
          slug: 'winter-set',
          price: '60.00',
          product_type: 'collection',
          product_type_label: 'Collection',
        }),
        candle_count: 3,
      },
    ],
    ...overrides,
  }
}

export function makeCandleDetail(overrides: Partial<CandleDetail> = {}): CandleDetail {
  return {
    ...makeItem({
      id: 2,
      title: 'Vintage Roadster Candle',
      slug: 'vintage-roadster-candle',
      description: 'A classic red roadster with golden wheels.',
      image: 'http://localhost/media/candles/roadster.webp',
      price: '28.00',
      tint: '#F3E1DB',
    }),
    scents: ['Unscented', 'Pine & cedar'],
    burn_time: '~25 hours',
    size: '14 × 7 × 8 cm',
    details: 'Soy wax, cotton wick.',
    story_title: '',
    story_text: '',
    flame: { x: 47.6, y: 86.5 },
    gallery: [{ image: 'http://localhost/media/candles/gallery/wheel.webp', label: 'Wheel detail' }],
    showcase_views: [],
    related: [makeItem({ id: 3, title: 'Carousel Candle', slug: 'carousel-candle', price: '42.00' })],
    ...overrides,
  }
}
