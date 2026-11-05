/** Response types for the Django REST API (see backend/README.md). */

/** `candle` = one piece, `set` = several pieces around a candle, `collection` = a bundle. */
export type ProductType = 'candle' | 'set' | 'collection'

/** A single candle, a candle set or a collection, as returned by the list endpoints. */
export interface ShopItem {
  id: number
  title: string
  slug: string
  description: string
  image: string
  /** Decimal string with 2 places, e.g. "24.00". */
  price: string
  stock: number
  /** Card background colour, e.g. "#E4ECDC". */
  tint: string
  is_available: boolean
  is_featured: boolean
  product_type: ProductType
  product_type_label: string
  created_at: string
  updated_at: string
}

export interface CollectionItem extends ShopItem {
  candle_count: number
}

export interface SlideLink {
  type: 'candle' | 'collection'
  slug: string
  price: string
  product_type_label: string
}

export interface HeroSlide {
  id: number
  title: string
  subtitle: string
  /** Absolute URL, or null if the slide has no image and its item was deleted. */
  image: string | null
  button_text: string
  link: SlideLink | null
}

/** Section images uploaded in the admin; null means "use the design's image". */
export interface ContentImages {
  made_before: string | null
  made_after: string | null
  video: string | null
  single_tile: string | null
  sets_tile: string | null
  custom_1: string | null
  custom_2: string | null
}

/** GET /api/site/: texts and images used across the site, edited in the admin. */
export interface SiteContent {
  studio_name: string
  accent_color: string
  currency: string
  ticker_messages: string[]
  hero_eyebrow: string
  hero_title: string
  hero_text: string
  hero_button_text: string
  hero_video_button_text: string
  collection_eyebrow: string
  collection_title: string
  made_title: string
  made_text: string
  step1_title: string
  step1_text: string
  step2_title: string
  step2_text: string
  step3_title: string
  step3_text: string
  video_title: string
  video_caption: string
  video_url: string
  single_tile_text: string
  sets_tile_text: string
  custom_title: string
  custom_text: string
  custom_button_text: string
  newsletter_title: string
  newsletter_text: string
  footer_text: string
  contact_email: string
  contact_phone: string
  instagram_handle: string
  // Shared by every product page
  price_note: string
  ships_in: string
  care_text: string
  shipping_text: string
  story_title: string
  story_text: string
  images: ContentImages
}

/** GET /api/home/ (site-wide texts come from GET /api/site/). */
export interface HomeData {
  slides: HeroSlide[]
  featured_candles: ShopItem[]
  featured_collections: CollectionItem[]
}

/** One view of the animated product showcase, edited on the product in the admin. */
export interface ShowcaseView {
  /** Absolute URL of a transparent cut-out. */
  image: string
  label: string
  short_label: string
  caption: string
  /** Ring and glow colour. */
  color: string
  /** Scene background colour. */
  tint: string
  group: 'side' | 'top' | 'bottom'
}

export interface GalleryImage {
  image: string
  label: string
}

/** Fields only present on the detail endpoints, for the product page. */
export interface ProductPageFields {
  scents: string[]
  burn_time: string
  size: string
  details: string
  /** Empty means "use the shared making-of text". */
  story_title: string
  story_text: string
  /** Wick position on the main image, in % from the left / bottom. Null: no lit view. */
  flame: { x: number; y: number } | null
  gallery: GalleryImage[]
  /** Empty: the page shows the regular gallery only. */
  showcase_views: ShowcaseView[]
  related: (ShopItem | CollectionItem)[]
}

export interface CandleSummary {
  title: string
  slug: string
  image: string
  price: string
  tint: string
  product_type_label: string
  is_available: boolean
}

/** GET /api/candles/<slug>/ */
export type CandleDetail = ShopItem & ProductPageFields

/** GET /api/collections/<slug>/ */
export type CollectionDetail = CollectionItem & ProductPageFields & { candles: CandleSummary[] }

export type ProductDetail = CandleDetail | CollectionDetail

/** The two kinds of product page, matching the API and the URLs. */
export type ProductKind = 'candle' | 'collection'

export interface TitledText {
  title: string
  text: string
}

/** GET /api/care/: the "Candle care & tips" page, edited in the admin. */
export interface CarePageData {
  /** May contain a line break ("
") chosen in the admin. */
  hero_title: string
  hero_text: string
  /** Absolute URL, or null: show the candlelit scene from the design. */
  hero_image: string | null
  tips_eyebrow: string
  tips: TitledText[]
  rituals_title: string
  rituals: TitledText[]
  fragrance_eyebrow: string
  fragrance_title: string
  fragrance_text: string
  fragrance_image: string | null
  fragrance_tips: { lead: string; text: string }[]
  /** In-stock candle shown as a "name · price" label on the fragrance picture. */
  fragrance_product: ShopItem | null
  faq_title: string
  faqs: { question: string; answer: string }[]
}

export type ChapterIllustration = 'soy' | 'plaster' | 'wick' | 'fragrance' | 'colour' | 'none'
export type CardIcon = 'braid' | 'wood' | 'clock' | 'scissors' | 'leaf' | 'drop'

/** One ingredient chapter of the "What's inside our candles" page. */
export interface IngredientChapter {
  /** Section id, e.g. "soy" for /ingredients#soy. */
  anchor: string
  nav_label: string
  title: string
  intro: string
  paragraphs: string[]
  illustration: ChapterIllustration
  /** Absolute URL of a photo that replaces the illustration, or null. */
  banner_image: string | null
  banner_color: string
  banner_text: 'dark' | 'light'
  cards_title: string
  points: { lead: string; text: string }[]
  questions: { question: string; answer: string }[]
  cards: { icon: CardIcon; title: string; text: string }[]
  swatches: { name: string; color: string; note: string }[]
}

/** GET /api/ingredients/ */
export interface IngredientsPageData {
  nav_title: string
  hero_eyebrow: string
  hero_title: string
  hero_text: string
  hero_link_text: string
  hero_image: string | null
  hero_image_label: string
  cta_title: string
  cta_text: string
  cta_button_text: string
  chapters: IngredientChapter[]
}

export interface GalleryPicture {
  id: number
  image: string
  caption: string
  /** Description for screen readers. */
  alt: string
  /** Candles shown in the picture, linked from the full-screen viewer. */
  products: Pick<ShopItem, 'title' | 'slug' | 'product_type'>[]
}

export interface DecorateRoom {
  title: string
  text: string
  /** Position of the room's picture in `gallery`, or null if it has none. */
  gallery_index: number | null
}

/** GET /api/decorate/ */
export interface DecoratePageData {
  hero_eyebrow: string
  /** May contain a line break ("
") chosen in the admin. */
  hero_title: string
  hero_text: string
  hero_link_text: string
  /** Absolute URL, or null: use the design's picture. */
  hero_image: string | null
  hero_image_alt: string
  story_title: string
  story_subtitle: string
  /** Paragraphs separated by blank lines; **double asterisks** mark bold words. */
  story_text: string
  gallery_title: string
  gallery_text: string
  cta_title: string
  cta_text: string
  cta_button_text: string
  cta_image: string | null
  rooms: DecorateRoom[]
  gallery: GalleryPicture[]
}
