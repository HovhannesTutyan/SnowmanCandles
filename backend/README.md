# Candle Shop — Django backend

Django 5.2 + Django REST Framework backend for the candle shop. It provides:

- a **Django admin** for managing single candles and collections (with images, price and stock)
- a **read-only REST API** under `/api/` for the React frontend (dev server: `http://localhost:5173`)

## Requirements

- Python 3.12+

## Setup

All commands are run from the `backend/` folder.

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

| Shell                    | Command                         |
| ------------------------ | ------------------------------- |
| Windows PowerShell       | `.venv\Scripts\Activate.ps1`    |
| Windows cmd              | `.venv\Scripts\activate.bat`    |
| Git Bash                 | `source .venv/Scripts/activate` |
| macOS / Linux            | `source .venv/bin/activate`     |

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and edit it:

```bash
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

Generate a secret key and paste it into `SECRET_KEY` in `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable               | Example                                     | Notes                                   |
| ---------------------- | ------------------------------------------- | --------------------------------------- |
| `SECRET_KEY`           | *(random string)*                           | **Required.** Never commit it.          |
| `DEBUG`                | `True`                                      | Use `False` in production.              |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`                       | Comma-separated.                        |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173`                     | Comma-separated; the React dev server.  |
| `DATABASE_URL`         | `postgres://user:pass@localhost:5432/shop`  | Optional. Defaults to SQLite.           |
| `TRANSLATION_PROVIDER` | `claude` or `google`                        | Optional. Turns on the admin's **Translate** button (see [Languages](#languages-english-armenian-russian)). |
| `TRANSLATION_API_KEY`  | *(API key)*                                 | Optional. The provider's key. Never commit it. |
| `TRANSLATION_MODEL`    | `claude-opus-5-5`                           | Optional, Claude only.                  |

**Switching to PostgreSQL:** run `pip install "psycopg[binary]"`, set `DATABASE_URL` in `.env`, then run the migrations again.

### 4. Run migrations

```bash
python manage.py migrate
```

Optional — load the six products and four hero slides from the homepage design
(prices are placeholders; safe to run more than once):

```bash
python manage.py seed_demo
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

- Admin: <http://127.0.0.1:8000/admin/>
- API root: <http://127.0.0.1:8000/api/>

Uploaded images are saved in `media/` and, while `DEBUG=True`, served at `/media/`.

## Running tests

```bash
python manage.py test
```

## Admin

Candles and Collections are separate sections. Both sections have:

- a thumbnail, price, stock and a coloured availability badge in the list
  (**In stock**, **Low stock** for 1–5 units, **Out of stock**)
- price and stock editable directly from the list
- an availability filter, a date filter and search by title/description
- a large image preview on the edit page
- a **Mark as out of stock** bulk action

Collections also show how many candles they contain, and use a two-pane selector for picking those candles.
A collection's price and stock are independent of its candles.

Slugs fill in automatically from the title. Duplicate titles get `-2`, `-3`, and so on.

## Homepage

Everything on the site is managed in the admin. The React app in `../frontend` reads the
site-wide texts from `GET /api/site/` and the homepage's slides and products from
`GET /api/home/`.

### Texts and section images (Home → Site content)

A single page with every editable text, grouped by section: studio name, accent colour,
currency, the scrolling ticker (one message per line), hero texts, the "How it's made"
steps and video, the "Shop by type" tiles, the custom-orders band, the newsletter, the
footer contact details, and the texts shared by every product page (see below).
"Shop by type" has two tiles: **Single candles** and **Candle sets**.

Every image on this page is optional. Leave one empty and the site uses the image from the
original design. The **Current** column next to each upload shows which one is in use.

### Carousel slides (Home → Hero slides)

The pieces that rotate on the hero pedestal, every 4 seconds.

1. Click **Add hero slide** and enter a title (the caption under the pedestal).
2. Link the slide to a **candle** or a **collection** (start typing to search). The caption then
   shows the item's type and price, and the item's image is used, unless you upload one.
   Use a **cut-out image with a transparent background** so it sits on the pedestal like in
   the design. A slide can link to a candle *or* a collection, not both.
3. Optional: a subtitle replaces the "type · price" line; button text adds a small link.
4. Set **Order** (lower numbers first) and keep **Is active** ticked to show the slide.

### Products in the grid (Shop → Candles / Collections)

- **Type** (candles only): **Single candle** for one piece (e.g. the roadster) or **Candle set**
  for more than one piece (e.g. the campfire: the logs are the candle, the snowmen are plaster).
  Shown as the badge on the card and under the hero pedestal.
- **Card colour**: the background behind the product image on its card.
- **Is featured** + **Featured order**: featured items appear in the hero's product row and the
  "winter collection" grid, lowest order first. You can also use the
  **Add to / Remove from homepage featured** bulk actions.

The homepage shows at most 8 featured candles and 8 featured collections.
Featured items that are out of stock are hidden automatically.
Product images also look best as cut-outs with a transparent background.

### `GET /api/site/`

```json
{
  "studio_name": "Celeb Candles",
  "accent_color": "#B4451A",
  "currency": "USD",
  "ticker_messages": ["Winter collection is here", "..."],
  "hero_title": "Little candles for the longest nights.",
  "care_text": "Trim the wick ...",
  "...": "every other text field",
  "images": { "made_before": null, "made_after": "http://.../media/homepage/after.webp", "...": null }
}
```

`images.*` is `null` when nothing was uploaded; the frontend then uses the design's image.

### `GET /api/home/`

```json
{
  "slides": [
    {
      "id": 1,
      "title": "Vintage Roadster Candle",
      "subtitle": "",
      "image": "http://127.0.0.1:8000/media/candles/2026/11/roadster.webp",
      "button_text": "",
      "link": { "type": "candle", "slug": "vintage-roadster-candle",
                "price": "28.00", "product_type_label": "Single candle" }
    }
  ],
  "featured_candles": [ /* same shape as /api/candles/ items */ ],
  "featured_collections": [ /* same shape as /api/collections/ items */ ]
}
```

A slide's `link` is `null` when it isn't linked; its `image` is `null` only if it has no
image of its own and its linked item was deleted.

## Product pages

Each candle and collection has its own page on the site (`/candles/<slug>`,
`/collections/<slug>`), linked from the homepage cards, the product row and the hero captions.

### Per product (Shop → Candles / Collections → a product)

- **Product page** section:
  - **Scents**: pick from the shared list (Shop → Scents); the first is selected by default.
    No scents = no scent choice on the page.
  - **Burn time** and **Size**: shown as facts under the "Add to cart" button. Leave empty to hide.
  - **Details**: materials, wax, wick… (first panel of the accordion).
  - **Making-of title / text**: this piece's story. Leave empty to use the shared one.
- **Lit view (optional)**: enter where the wick is on the main image, in % from the left and
  from the bottom, and save. The preview shows a dot where the flame will be. The page then
  gets a "Lit" view with an animated flame and snow, and the making-of section shows the
  candle lit.
- **Extra photos**: add close-ups or photos of the lit candle at the bottom of the page. Each
  needs a short label (e.g. "Wheel detail") and appears as a gallery thumbnail.
- **Showcase views (optional)**: the animated viewer at the top of the product page. Add one
  view per angle: a transparent cut-out (all the same size, product at the bottom of the image),
  a big label, button text, caption, **ring colour**, **background colour**, **view type**
  (side / from above / underneath) and order. The selected view slides onto a glowing ring and
  the whole scene takes its colours. Without views the product page shows the regular gallery
  only. (Snowmen by the Campfire has one; `seed_demo` adds it.)

### Shared by every product (Home → Site content → Product pages)

The note next to the price, "Ships in", **Candle care**, **Shipping & returns**, and the default
making-of title and text.

"You might also love" picks up to 4 other in-stock products automatically: for a candle,
other candles of the same type first; for a collection, other collections first.

## Candle care page (Care → Candle care page)

The `/candle-care` page on the site, linked from the header, the footer, the homepage's
"How it's made" section and the "Candle care" panel on every product page. Everything on it
is edited on this one admin page:

- **Hero**: title (press Enter where the line should break), intro text, optional wide photo.
- **Section headings** for the tips, the care rituals and the FAQ.
- **Fragrance section**: heading, text, optional photo, and an optional **featured candle**
  shown as a "name · price" label linking to its product page (hidden while it's sold out).
- **Tips**, **Care rituals**, **Fragrance points** and **FAQs**: lists at the bottom of the
  page. Add, edit or delete items; the **Order** field sets their position (tips are
  numbered 01, 02, … in that order). A list left empty hides its section.

Without photos, the page shows the candlelit scenes from the design, made from product
cut-outs. The page starts with the design's content (adapted to candles).

## Ingredients page (Ingredients → …)

The `/ingredients` page ("What's inside our candles"), linked from the header and the footer.

- **Ingredients page**: the hero (title, text, "Start with the wax" link, optional photo and its
  label) and the closing call to action.
- **Chapters**: one per ingredient (Soy wax, Plaster, Wick, Fragrance, Colour to start with).
  Add, hide (untick **Is published**) or reorder them (**Order**) from the list. Each chapter has:
  - a **banner**: big title, short intro, a drawn **illustration** or your own **photo**, a
    background colour and light/dark text;
  - **text** (empty line between paragraphs) and optional lists at the bottom of its page:
    **bullet points**, **questions** (expandable, shown next to the text), **cards** (with an
    icon and the cards title above them) and **colour swatches** (the Colour banner's stripes
    use these colours).
  - The **anchor** sets the section address, e.g. `soy` → `/ingredients#soy`.

## Decorate page (Decorate → …)

The `/decorate` page ("Decorate with candles"), linked from the header ("Inspiration"), the
footer and the homepage's "Shop by type" section. Every section is editable:

- **Decorate page**: the hero (title — press Enter for the line break — text, gallery link,
  tall picture and its description), the story (title, subtitle and text: an empty line
  between paragraphs, `**double asterisks**` for bold words), the gallery heading, the closing
  call to action with its picture, and the **room cards** (Living room, Bedroom, …) at the
  bottom: title, short text, order and the **gallery picture** the card shows and opens.
- **Gallery images**: upload square pictures (about 1200 × 1200 px), with a caption and a
  description, and pick the **candles in this picture** — they appear as links in the
  full-screen viewer. Reorder with **Order**, hide with **Is published**.

Without uploads, the hero and closing pictures fall back to the design's. The 16 gallery
pictures from the design are demo content loaded by `python manage.py seed_demo`.

## Languages (English, Armenian, Russian)

The site is in **Armenian** (the default, at `/`), **English** (`/en/…`) and **Russian**
(`/ru/…`). Every text you can edit in the admin has three boxes: the **English** one
(required) and the **Armenian** and **Russian** ones under it. The interface texts written in
the code (buttons, menus, labels) are translated in `frontend/src/i18n/messages/`.

**In the admin**

- Each translated field is a small group: **EN**, **HY**, **RU**. An empty Armenian or Russian
  box is marked **Missing**; until it's filled, the site shows the English text there.
- The bar at the top of every form shows how many translations are missing, a filter
  (*All languages*, *English + Armenian*, *English + Russian*, *English only*) and
  **Translate missing**. Each group also has its own **Translate** button.
- Translations are filled into the form as **Draft – check**: read them, fix anything, then
  **Save**. Nothing is saved before you press Save.
- The admin home page has a **Translations** box, and **Missing translations** lists every item
  that still needs work, with a link to the page where it's edited. Product, slide, chapter and
  gallery lists have a **Translations** column.

**Turning on automatic translation.** The Translate buttons stay disabled until a service is
set in `.env`, then restart the server:

```ini
TRANSLATION_PROVIDER=claude      # or: google
TRANSLATION_API_KEY=your-key
```

- `claude` uses the Anthropic API (also run `pip install anthropic`). It is told about the shop:
  natural copy, "candle" wording, Markdown bold and line breaks kept. Default model
  `claude-opus-5-5` (`TRANSLATION_MODEL` to change it).
- `google` uses Google Cloud Translation (v2, API key). Cheaper, more literal.

Machine translation is a draft, especially for Armenian: have a native speaker read new texts.

**Built-in translations.** Armenian and Russian versions of all the current texts (pages, demo
products, gallery, care tips…) are in `languages/content_translations.json`. They were filled in
when the languages were added (a migration), `seed_demo` uses them, and
`python manage.py fill_translations` fills any empty translation they cover — it never
overwrites one you wrote.

**API.** Add `?lang=hy`, `?lang=ru` or `?lang=en` (the default) to any endpoint; translated
fields come back in that language, falling back to English when a translation is empty.

## API

All endpoints are read-only (`GET`). Add `?lang=hy|en|ru` for a language
(see [Languages](#languages-english-armenian-russian)).

| Endpoint                         | Description                                          |
| -------------------------------- | ---------------------------------------------------- |
| `/api/candles/`                  | List candles                                         |
| `/api/candles/<slug>/`           | Candle detail for the product page (see below)       |
| `/api/collections/`              | List collections (includes `candle_count`)           |
| `/api/collections/<slug>/`       | Collection detail, also with its nested `candles`    |
| `/api/site/`                     | Site-wide texts and images (see [Homepage](#homepage)) |
| `/api/home/`                     | Homepage slides and featured products; not paginated |
| `/api/care/`                     | The candle care page: texts, photos, tips, rituals, fragrance points, FAQs |
| `/api/ingredients/`              | The ingredients page: hero, closing texts and published chapters |
| `/api/decorate/`                 | The decorate page: texts, rooms (with `gallery_index`), published gallery pictures |

The detail endpoints add the product page fields to the list item shape:

```json
{
  "...": "every list field",
  "scents": ["Unscented", "Pine & cedar"],
  "burn_time": "~25 hours",
  "size": "14 × 7 × 8 cm",
  "details": "Soy wax, cotton wick.",
  "story_title": "",
  "story_text": "",
  "flame": { "x": 47.6, "y": 86.5 },
  "gallery": [{ "image": "http://.../media/candles/gallery/2026/11/wheel.webp", "label": "Wheel detail" }],
  "related": [ /* up to 4 list items, candles and/or collections */ ]
}
```

`showcase_views` lists the showcase's views in order (`image`, `label`, `short_label`, `caption`,
`color`, `tint`, `group`). `flame` is `null` when no wick position is set. Empty `story_*` fields mean "use the shared text".

List query parameters (they can be combined):

| Param        | Example              | Effect                                 |
| ------------ | -------------------- | -------------------------------------- |
| `available`  | `?available=true`    | Only items with stock > 0              |
| `featured`   | `?featured=true`     | Only items marked as homepage featured |
| `type`       | `?type=set`          | Candles only: `candle` (single) or `set` |
| `min_price`  | `?min_price=10`      | Price ≥ value                          |
| `max_price`  | `?max_price=30`      | Price ≤ value                          |
| `ordering`   | `?ordering=-price`   | `price`, `-price`, `created_at`, `-created_at` (default: newest first) |
| `page`       | `?page=2`            | 12 items per page                      |

An invalid filter value (for example `?min_price=abc`) returns `400 Bad Request`.

Example item:

```json
{
  "id": 1,
  "title": "Vanilla Dream",
  "slug": "vanilla-dream",
  "description": "...",
  "image": "http://127.0.0.1:8000/media/candles/2026/11/vanilla.jpg",
  "price": "12.50",
  "stock": 10,
  "tint": "#F3E1DB",
  "is_available": true,
  "is_featured": false,
  "created_at": "2026-11-02T10:00:00Z",
  "updated_at": "2026-11-02T10:00:00Z",
  "product_type": "candle",
  "product_type_label": "Single candle"
}
```

Collections return the same keys, with `"product_type": "collection"` and a `candle_count`.

List responses are paginated: `{"count", "next", "previous", "results": [...]}`.
