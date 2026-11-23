# HugCrafts — React frontend

The shop's storefront, built with Vite, React 19, React Router and TypeScript from the
"Home page" and "Product page" design mockups. All content comes from the Django backend
(`../backend`), so every text, image, slide and product can be changed in the Django admin.

| Route                 | Page                                   | Data                         |
| --------------------- | -------------------------------------- | ---------------------------- |
| `/`                   | Homepage                               | `/api/site/`, `/api/home/`   |
| `/candles/<slug>`     | Product page for a single candle / set | `/api/candles/<slug>/`       |
| `/collections/<slug>` | Product page for a collection          | `/api/collections/<slug>/`   |
| `/candle-care`        | Candle care & tips                     | `/api/care/`                 |
| `/ingredients`        | What's inside our candles              | `/api/ingredients/`          |
| `/decorate`           | Decorate with candles (inspiration)    | `/api/decorate/`             |
| anything else         | "Page not found"                       |                              |

Site-wide texts (`/api/site/`) load once and are shared by every page.

## Requirements

- Node.js 20+
- The Django backend running on <http://127.0.0.1:8000> (see `../backend/README.md`)

## Getting started

```bash
npm install
npm run dev
```

Open <http://localhost:5173>. In development Vite forwards `/api` and `/media` to Django
(see `vite.config.ts`), so no extra configuration is needed.

To see the design's products straight away, run `python manage.py seed_demo` in `../backend`.

## Scripts

| Command              | What it does                                  |
| -------------------- | --------------------------------------------- |
| `npm run dev`        | Start the dev server with hot reload          |
| `npm test`           | Run the tests once (Vitest + Testing Library) |
| `npm run test:watch` | Run the tests in watch mode                   |
| `npm run lint`       | Lint with oxlint                              |
| `npm run build`      | Type-check and build to `dist/`               |
| `npm run preview`    | Serve the production build locally            |

## Configuration

Copy `.env.example` to `.env` to override settings.

| Variable            | Default | Notes                                                        |
| ------------------- | ------- | ------------------------------------------------------------ |
| `VITE_API_BASE_URL` | *(empty)* | Backend URL for production builds, e.g. `https://api.example.com`. Add the site's URL to `CORS_ALLOWED_ORIGINS` in the backend `.env`. |

## Project structure

```
src/
  main.tsx        Providers + router
  router.tsx      Routes, repeated for each language: "/" (Armenian), "/en/…", "/ru/…"
  i18n/           Languages: locales.ts (prefixes, names), messages/en|hy|ru.ts (interface
                  texts), context.ts (useI18n), LocaleRoot, Link (keeps the language)
  api/            Typed API client (client.ts) and response types (types.ts)
  context/        Site content (useSite) and basket (useCart: lines, quantities, slide-in panel)
  hooks/          useAsync (loading / error / retry), useFlash, useMediaQuery, usePrefersReducedMotion
  lib/            Price formatting, product URLs/keys, design image fallbacks, helpers
  components/
    layout/       SiteLayout (loads site content), Ticker, Header (menu, cart badge),
                  LanguageSwitcher, Footer
    home/         Hero, HeroShowcase (carousel), ProductTrain, CollectionGrid,
                  ProductCard, HowItsMade, ShopByType, CustomBand, Newsletter, Snowfall
    product/      ProductShowcase (animated viewer), ProductGallery, Flame, BuyBox, Accordion,
                  MakingOf, RelatedProducts
    care/         Scenes (candlelit illustrations), Faq
    ingredients/  ChapterSection, Illustrations (drawn banners), Disclosure, CardIcon
    decorate/     GallerySlider (drag/swipe/keys), Lightbox (full-screen viewer)
    common/       SectionNav (sticky section bar), RichText (**bold** in admin text)
    cart/         CartPanel (slide-in basket), CartLineItem (row with quantity buttons), CartTotals
    StatusScreen  Loading, error and message screens
  pages/          HomePage, ProductPage, CareTipsPage, IngredientsPage, DecoratePage, BasketPage, CheckoutPage,
                  NotFoundPage, RouteErrorPage
  styles/         global.css: design tokens and shared animation utilities
  assets/design/  Images from the original design (used as fallbacks)
  test/           Test setup, fixtures and renderApp (whole app with a mocked API)
```

Each component has its own CSS Module with the exact colours, sizes and spacing from the design.

## Where each part of the page comes from

| Section            | Managed in the admin under                                       |
| ------------------ | ---------------------------------------------------------------- |
| Ticker, hero texts, "How it's made", tiles, custom band, newsletter, footer | **Home → Site content** (images are optional; empty = design image) |
| Rotating pieces on the hero pedestal | **Home → Hero slides** |
| Product row and "winter collection" grid | **Shop → Candles / Collections** with **Is featured** ticked |
| Accent colour and currency | **Home → Site content → Brand** |
| Product page: showcase views, scents, burn time, size, details, making-of, lit view, extra photos | **Shop → Candles / Collections**, on each product |
| Product page: price note, ships in, candle care, shipping & returns | **Home → Site content → Product pages** |
| Candle care page: all texts, photos, tips, rituals, fragrance points, FAQs | **Care → Candle care page** |
| Ingredients page: hero, closing texts | **Ingredients → Ingredients page** |
| Ingredients page: chapters (banner, text, points, questions, cards, swatches) | **Ingredients → Chapters** |
| Decorate page: hero, story, room cards, gallery heading, closing section | **Decorate → Decorate page** |
| Decorate page: gallery pictures (and the candles shown in each) | **Decorate → Gallery images** |

## Languages

Armenian is the default at `/`; English is under `/en/` and Russian under `/ru/` (the same
pages: `/candle-care`, `/en/candle-care`, `/ru/candle-care`). The header's language menu opens
the current page in another language.

- **Texts from the admin** come from the API in the page's language (`?lang=hy|en|ru`).
- **Texts in the code** (buttons, menus, labels, page titles) are in
  `src/i18n/messages/en.ts`, `hy.ts` and `ru.ts`. Add a text to `en.ts` first: TypeScript then
  points to the other two until they have it too.
- In components, use `const { t } = useI18n()` for texts, and `Link` from `src/i18n/Link`
  (not from `react-router`) so links stay in the current language.
- Fonts: the design fonts have no Armenian or Cyrillic letters. Cyrillic comes from Onest
  (Google Fonts); Armenian from Noto Sans Armenian, bundled in `src/assets/fonts/` and set
  to 85% size (`size-adjust` in `styles/global.css`) because Armenian words run wider. Change
  that one number to make all Armenian text bigger or smaller.

## Notes

- Animations follow the design and switch off for visitors with *reduce motion* enabled.
  The carousel then stays on one slide, and the bars under it can still be clicked.
- **Basket and checkout:** "Add to basket" opens a slide-in basket (also from the bag icon), with
  quantity buttons, remove, and links to `/basket` and `/checkout`. The basket is kept in the
  browser (`localStorage`); prices and stock are fetched from `POST /api/cart/` and checked again
  when the order is placed (`POST /api/orders/`). No online payment: orders go to the admin and
  the shop calls the customer. Delivery is free (1–2 days).
- Search, the newsletter form and "Request a custom piece" are visual only for now.
  The shop-by-type tiles and "View all pieces" scroll within the homepage until shop pages exist.
- Deploying: product URLs like `/candles/<slug>` are handled in the browser, so the web server
  must serve `index.html` for any path that isn't a file ("SPA fallback").
