"""What the server sends for each page address: title, description, links, preview tags,
structured data for Google, and the page's text as plain HTML.

The React app replaces the text with the real page once it starts, so this is mostly for
search engines and link previews (Telegram, WhatsApp, Facebook…), which read the HTML
without running JavaScript.
"""

import re
from dataclasses import dataclass, field
from decimal import Decimal

from django.conf import settings
from django.db.models import Count
from django.utils import translation

from care.models import CarePage
from decorate.models import DecoratePage, GalleryImage
from home.models import HomePageContent
from ingredients.models import Chapter, IngredientsPage
from shop.models import Candle, Collection

from .models import SeoSettings
from .texts import text

# Same as frontend/src/i18n/locales.ts: Armenian at the root, English and Russian prefixed.
LANGS = ("hy", "en", "ru")
DEFAULT_LANG = "hy"
PREFIX = {"hy": "", "en": "/en", "ru": "/ru"}
HTML_LANG = {"hy": "hy-AM", "en": "en-US", "ru": "ru-RU"}
OG_LOCALE = {"hy": "hy_AM", "en": "en_US", "ru": "ru_RU"}
NATIVE_NAMES = {"hy": "Հայերեն", "en": "English", "ru": "Русский"}

DESCRIPTION_LENGTH = 160
FEATURED_FIRST = ["-is_featured", "featured_order", "-created_at"]
RELATED_LIMIT = 4
CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£"}
WHOLE_NUMBER_CURRENCIES = {"AMD": "֏", "RUB": "₽"}

SIMPLE_PAGES = {
    "/candle-care": "care",
    "/ingredients": "ingredients",
    "/decorate": "decorate",
    "/basket": "basket",
    "/checkout": "checkout",
}
PRODUCT_PATH = re.compile(r"^/(candles|collections)/([^/]+)$")


@dataclass
class Page:
    lang: str
    path: str  # without the language prefix, e.g. "/candles/holly"
    kind: str
    title: str = ""
    description: str = ""
    status: int = 200
    noindex: bool = False
    og_type: str = "website"
    image: str = ""
    image_alt: str = ""
    product_meta: dict = field(default_factory=dict)
    json_ld: list = field(default_factory=list)
    body: dict = field(default_factory=dict)  # context for the page's text template
    canonical: str = ""
    alternates: list = field(default_factory=list)  # [(hreflang, url)]
    languages: list = field(default_factory=list)  # [(lang, native name, url, is_current)]

    @property
    def html_lang(self):
        return HTML_LANG[self.lang]

    @property
    def og_locale(self):
        return OG_LOCALE[self.lang]

    @property
    def og_locale_alternates(self):
        return [OG_LOCALE[lang] for lang in LANGS if lang != self.lang]


# Addresses ----------------------------------------------------------------------------


def split_locale(pathname: str) -> tuple[str, str]:
    """("/ru/decorate") -> ("ru", "/decorate"); trailing slashes are dropped."""
    for lang, prefix in PREFIX.items():
        if prefix and (pathname == prefix or pathname.startswith(prefix + "/")):
            pathname = pathname[len(prefix):]
            break
    else:
        lang = DEFAULT_LANG
    path = pathname.rstrip("/") or "/"
    return lang, path


def localize(path: str, lang: str) -> str:
    prefix = PREFIX[lang]
    if not prefix:
        return path
    return prefix if path == "/" else prefix + path


def site_origin(request) -> str:
    """The public address, e.g. "https://hugcrafts.am" (SITE_URL, else from the request)."""
    if settings.SITE_URL:
        return settings.SITE_URL.rstrip("/")
    return f"{request.scheme}://{request.get_host()}"


# Small helpers ------------------------------------------------------------------------


def plain(value: str) -> str:
    return " ".join((value or "").split())


def clip(value: str, length: int = DESCRIPTION_LENGTH) -> str:
    """Shortened at a word, for meta descriptions."""
    value = plain(value)
    if len(value) <= length:
        return value
    cut = value[: length - 1]
    if value[length - 1] != " ":  # don't end on half a word
        cut = cut.rsplit(" ", 1)[0]
    cut = cut.rstrip(",;:—-– ")
    return cut + "…"


def paragraphs(value: str) -> list[str]:
    value = (value or "").replace("\r\n", "\n")
    return [plain(p) for p in re.split(r"\n\s*\n", value) if p.strip()]


def format_price(amount: Decimal, currency: str) -> str:
    if currency in CURRENCY_SYMBOLS:
        return f"{CURRENCY_SYMBOLS[currency]}{amount:,.2f}"
    if currency in WHOLE_NUMBER_CURRENCIES:
        return f"{amount:,.0f} {WHOLE_NUMBER_CURRENCIES[currency]}"
    return f"{amount:,.2f} {currency}"


def seo_text(obj, field_name: str, lang: str) -> str:
    """The SEO field in exactly this language (no fallback to English: an empty Armenian
    field should give the automatic Armenian text, not the English one)."""
    return plain(getattr(obj, f"{field_name}_{lang}", "") or "")


def auto_product_title(item, studio: str) -> str:
    return f"{item.title} — {studio}"


def auto_page_title(lang: str, key: str, studio: str) -> str:
    if key == "home":
        return text(lang, "home_title", studio=studio)
    return f"{text(lang, f'{key}_title')} — {studio}"


def auto_page_description(lang: str, key: str, content) -> str:
    if key == "home":
        return clip(content.hero_text)
    return text(lang, f"{key}_description")


# The page ----------------------------------------------------------------------------


class PageBuilder:
    def __init__(self, request, pathname: str):
        self.lang, self.path = split_locale(pathname)
        self.origin = site_origin(request)
        self.content = HomePageContent.load()
        self.seo = SeoSettings.load()

    def url(self, path: str, lang: str | None = None) -> str:
        return self.origin + localize(path, lang or self.lang)

    def absolute(self, file_field) -> str:
        if not file_field:
            return ""
        url = file_field.url
        return url if url.startswith(("http://", "https://")) else self.origin + url

    def product_path(self, item) -> str:
        kind = "candles" if isinstance(item, Candle) else "collections"
        return f"/{kind}/{item.slug}"

    def build(self) -> Page:
        with translation.override(self.lang):
            page = self._build()
        page.languages = [
            (lang, NATIVE_NAMES[lang], self.url(page.path, lang), lang == page.lang)
            for lang in LANGS
        ]
        if not page.noindex:
            page.canonical = self.url(page.path)
            page.alternates = [(lang, self.url(page.path, lang)) for lang in LANGS]
            page.alternates.append(("x-default", self.url(page.path, DEFAULT_LANG)))
        page.body.update(self.common_body(page))
        return page

    def _build(self) -> Page:
        if self.path == "/":
            return self.home()
        match = PRODUCT_PATH.match(self.path)
        if match:
            model = Candle if match[1] == "candles" else Collection
            item = model.objects.filter(slug=match[2]).first()
            return self.product(item) if item else self.not_found(product=True)
        kind = SIMPLE_PAGES.get(self.path)
        if kind in {"care", "ingredients", "decorate"}:
            return getattr(self, kind)()
        if kind in {"basket", "checkout"}:
            return self.private_page(kind)
        return self.not_found()

    # Pieces shared by every page ---------------------------------------------------

    def common_body(self, page: Page) -> dict:
        c = self.content
        t = lambda key: text(self.lang, key)  # noqa: E731
        return {
            "studio": c.studio_name,
            "home_url": localize("/", self.lang),
            "nav": [
                (t("shop"), localize("/", self.lang) + "#shop"),
                (text(self.lang, "decorate_title"), localize("/decorate", self.lang)),
                (text(self.lang, "ingredients_title"), localize("/ingredients", self.lang)),
                (text(self.lang, "care_title"), localize("/candle-care", self.lang)),
            ],
            "nav_label": t("main_menu"),
            "language_label": t("language"),
            "languages": [
                (native, localize(page.path, lang), lang, current)
                for lang, native, _url, current in page.languages
            ],
            "footer_text": c.footer_text,
            "contact_email": c.contact_email,
            "contact_phone": c.contact_phone,
            "instagram": c.instagram_handle.lstrip("@") if c.instagram_handle else "",
        }

    def share_image(self) -> str:
        if self.seo.share_image:
            return self.absolute(self.seo.share_image)
        item = (
            Candle.objects.filter(is_featured=True).order_by(*FEATURED_FIRST[1:]).first()
            or Candle.objects.order_by(*FEATURED_FIRST).first()
        )
        return self.absolute(item.image) if item else ""

    def organization(self) -> dict:
        c = self.content
        data = {
            "@type": "OnlineStore",
            "@id": self.origin + "/#organization",
            "name": c.studio_name,
            "url": self.url("/"),
        }
        if c.footer_text:
            data["description"] = plain(c.footer_text)
        if c.contact_email:
            data["email"] = c.contact_email
        if c.contact_phone:
            data["telephone"] = c.contact_phone
        if c.instagram_handle:
            data["sameAs"] = [f"https://www.instagram.com/{c.instagram_handle.lstrip('@')}/"]
        return data

    def breadcrumbs(self, name: str, path: str) -> dict:
        return {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": text(self.lang, "home"),
                 "item": self.url("/")},
                {"@type": "ListItem", "position": 2, "name": name, "item": self.url(path)},
            ],
        }

    def page_texts(self, key: str) -> tuple[str, str]:
        studio = self.content.studio_name
        title = seo_text(self.seo, f"{key}_title", self.lang) or auto_page_title(
            self.lang, key, studio
        )
        description = seo_text(self.seo, f"{key}_description", self.lang) or auto_page_description(
            self.lang, key, self.content
        )
        return title, description

    def card(self, item) -> dict:
        if isinstance(item, Collection):
            type_label = text(self.lang, "collection")
        else:
            type_label = text(self.lang, item.product_type)
        return {
            "title": item.title,
            "url": localize(self.product_path(item), self.lang),
            "image": item.image.url if item.image else "",
            "price": format_price(item.price, self.content.currency),
            "type": type_label,
            "available": item.is_available,
        }

    def faq(self, pairs) -> dict | None:
        entries = [
            {"@type": "Question", "name": plain(q),
             "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
            for q, a in pairs if plain(q) and plain(a)
        ]
        return {"@type": "FAQPage", "mainEntity": entries} if entries else None

    # Pages -----------------------------------------------------------------------

    def home(self) -> Page:
        c = self.content
        title, description = self.page_texts("home")
        candles = list(Candle.objects.order_by(*FEATURED_FIRST))
        collections = list(Collection.objects.order_by(*FEATURED_FIRST))
        website = {
            "@type": "WebSite",
            "@id": self.origin + "/#website",
            "name": c.studio_name,
            "url": self.url("/"),
            "inLanguage": HTML_LANG[self.lang],
            "publisher": {"@id": self.origin + "/#organization"},
        }
        return Page(
            lang=self.lang, path="/", kind="home", title=title, description=description,
            image=self.share_image(), image_alt=c.studio_name,
            json_ld=[self.organization(), website],
            body={
                "eyebrow": c.hero_eyebrow,
                "heading": c.hero_title,
                "intro": c.hero_text,
                "collection_title": c.collection_title,
                "products": [self.card(item) for item in [*candles, *collections]],
                "made_title": c.made_title,
                "made_text": c.made_text,
                "steps": [
                    (c.step1_title, c.step1_text),
                    (c.step2_title, c.step2_text),
                    (c.step3_title, c.step3_text),
                ],
                "custom_title": c.custom_title,
                "custom_text": c.custom_text,
                "story_title": c.story_title,
                "story_text": paragraphs(c.story_text),
                "delivery_text": c.delivery_text,
            },
        )

    def product(self, item) -> Page:
        c = self.content
        studio = c.studio_name
        path = self.product_path(item)
        is_collection = isinstance(item, Collection)
        type_label = text(self.lang, "collection" if is_collection else item.product_type)
        title = seo_text(item, "seo_title", self.lang) or auto_product_title(item, studio)
        description = seo_text(item, "seo_description", self.lang) or clip(item.description)
        gallery = list(item.gallery.all())
        images = [self.absolute(item.image)] + [self.absolute(g.image) for g in gallery]
        images = [url for url in images if url]
        availability = "InStock" if item.is_available else "OutOfStock"
        price = f"{item.price:.2f}"

        offer = {
            "@type": "Offer",
            "url": self.url(path),
            "price": price,
            "priceCurrency": c.currency,
            "availability": f"https://schema.org/{availability}",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {"@id": self.origin + "/#organization"},
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {"@type": "MonetaryAmount", "value": 0, "currency": c.currency},
                "shippingDestination": {
                    "@type": "DefinedRegion", "addressCountry": self.seo.delivery_country,
                },
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1,
                                     "unitCode": "DAY"},
                    "transitTime": {"@type": "QuantitativeValue",
                                    "minValue": self.seo.delivery_days_min,
                                    "maxValue": max(self.seo.delivery_days_min,
                                                    self.seo.delivery_days_max),
                                    "unitCode": "DAY"},
                },
            },
        }
        product = {
            "@type": "Product",
            "name": item.title,
            "description": plain(item.description),
            "sku": item.slug,
            "url": self.url(path),
            "category": type_label,
            "brand": {"@type": "Brand", "name": studio},
            "offers": offer,
        }
        if images:
            product["image"] = images
        if item.size:
            product["size"] = item.size

        includes = []
        if is_collection:
            includes = [self.card(candle) for candle in item.candles.all()]
        related = self.related(item)

        return Page(
            lang=self.lang, path=path, kind="product", title=title, description=description,
            og_type="product", image=images[0] if images else self.share_image(),
            image_alt=item.title,
            product_meta={"price": price, "currency": c.currency,
                          "availability": "in stock" if item.is_available else "out of stock"},
            json_ld=[self.organization(), product, self.breadcrumbs(item.title, path)],
            body={
                "home_label": text(self.lang, "home"),
                "breadcrumb_label": text(self.lang, "breadcrumb"),
                "heading": item.title,
                "type": type_label,
                "image": item.image.url if item.image else "",
                "gallery": [(g.image.url, f"{item.title}: {g.label}") for g in gallery if g.image],
                "price": format_price(item.price, c.currency),
                "availability": text(self.lang, "in_stock" if item.is_available else "sold_out"),
                "delivery_text": c.delivery_text,
                "price_note": c.price_note,
                "description": paragraphs(item.description),
                "facts": [
                    (text(self.lang, "burn_time"), item.burn_time),
                    (text(self.lang, "size"), item.size),
                ],
                "scents_label": text(self.lang, "scents"),
                "scents": [scent.name for scent in item.scents.all()],
                "details_label": text(self.lang, "details"),
                "details": paragraphs(item.details),
                "includes_label": text(self.lang, "includes"),
                "includes": includes,
                "story_title": item.story_title or c.story_title,
                "story_text": paragraphs(item.story_text or c.story_text),
                "care_label": text(self.lang, "care"),
                "care_text": c.care_text,
                "shipping_label": text(self.lang, "shipping"),
                "shipping_text": c.shipping_text,
                "related_label": text(self.lang, "related"),
                "related": related,
            },
        )

    def related(self, item) -> list[dict]:
        candles = Candle.objects.filter(stock__gt=0).order_by(*FEATURED_FIRST)
        collections = Collection.objects.filter(stock__gt=0).order_by(*FEATURED_FIRST)
        if isinstance(item, Candle):
            groups = [candles.exclude(pk=item.pk), collections]
        else:
            groups = [collections.exclude(pk=item.pk), candles]
        found = []
        for queryset in groups:
            found += list(queryset[: RELATED_LIMIT - len(found)])
            if len(found) >= RELATED_LIMIT:
                break
        return [self.card(other) for other in found]

    def care(self) -> Page:
        CarePage.load()
        page = CarePage.objects.prefetch_related("tips", "rituals", "fragrance_tips", "faqs").get(pk=1)
        title, description = self.page_texts("care")
        faqs = list(page.faqs.all())
        json_ld = [self.organization(), self.breadcrumbs(text(self.lang, "care_title"), "/candle-care")]
        if faq := self.faq((f.question, f.answer) for f in faqs):
            json_ld.append(faq)
        return Page(
            lang=self.lang, path="/candle-care", kind="care", title=title,
            description=description,
            image=self.absolute(page.hero_image) or self.share_image(), image_alt=page.hero_title,
            json_ld=json_ld,
            body={
                "heading": page.hero_title,
                "intro": page.hero_text,
                "tips_title": page.tips_eyebrow,
                "tips": [(tip.title, tip.text) for tip in page.tips.all()],
                "rituals_title": page.rituals_title,
                "rituals": [(r.title, r.text) for r in page.rituals.all()],
                "fragrance_title": page.fragrance_title,
                "fragrance_text": paragraphs(page.fragrance_text),
                "fragrance_tips": [(f.lead, f.text) for f in page.fragrance_tips.all()],
                "faq_title": page.faq_title,
                "faqs": [(f.question, f.answer) for f in faqs],
            },
        )

    def ingredients(self) -> Page:
        page = IngredientsPage.load()
        chapters = list(
            Chapter.objects.filter(is_published=True).prefetch_related(
                "points", "questions", "cards", "swatches"
            )
        )
        title, description = self.page_texts("ingredients")
        json_ld = [self.organization(),
                   self.breadcrumbs(text(self.lang, "ingredients_title"), "/ingredients")]
        pairs = [(q.question, q.answer) for ch in chapters for q in ch.questions.all()]
        if faq := self.faq(pairs):
            json_ld.append(faq)
        return Page(
            lang=self.lang, path="/ingredients", kind="ingredients", title=title,
            description=description,
            image=self.absolute(page.hero_image) or self.share_image(), image_alt=page.hero_title,
            json_ld=json_ld,
            body={
                "heading": page.hero_title,
                "intro": page.hero_text,
                "chapters": [
                    {
                        "anchor": ch.anchor,
                        "title": ch.title,
                        "intro": ch.intro,
                        "paragraphs": ch.paragraphs,
                        "points": [(p.lead, p.text) for p in ch.points.all()],
                        "questions": [(q.question, q.answer) for q in ch.questions.all()],
                        "cards_title": ch.cards_title,
                        "cards": [(card.title, card.text) for card in ch.cards.all()],
                        "swatches": [s.name for s in ch.swatches.all()],
                    }
                    for ch in chapters
                ],
                "cta_title": page.cta_title,
                "cta_text": page.cta_text,
            },
        )

    def decorate(self) -> Page:
        page = DecoratePage.load()
        title, description = self.page_texts("decorate")
        gallery = list(GalleryImage.objects.filter(is_published=True))
        image = self.absolute(page.hero_image) or (
            self.absolute(gallery[0].image) if gallery else self.share_image()
        )
        return Page(
            lang=self.lang, path="/decorate", kind="decorate", title=title,
            description=description, image=image, image_alt=page.hero_image_alt or page.hero_title,
            json_ld=[self.organization(),
                     self.breadcrumbs(text(self.lang, "decorate_title"), "/decorate")],
            body={
                "eyebrow": page.hero_eyebrow,
                "heading": page.hero_title,
                "intro": page.hero_text,
                "story_title": page.story_title,
                "story_subtitle": page.story_subtitle,
                "story_text": paragraphs(page.story_text),
                "rooms": [(room.title, room.text) for room in page.rooms.all()],
                "gallery_title": page.gallery_title,
                "gallery_text": page.gallery_text,
                "gallery": [(g.image.url, g.alt or g.caption, g.caption) for g in gallery if g.image],
                "cta_title": page.cta_title,
                "cta_text": page.cta_text,
            },
        )

    def private_page(self, kind: str) -> Page:
        """Basket and checkout: useful to people, not to search results."""
        heading = text(self.lang, f"{kind}_title")
        return Page(
            lang=self.lang, path=f"/{kind}", kind="simple", noindex=True,
            title=f"{heading} — {self.content.studio_name}",
            image=self.share_image(), body={"heading": heading},
        )

    def not_found(self, product: bool = False) -> Page:
        prefix = "product_not_found" if product else "not_found"
        heading = text(self.lang, f"{prefix}_title")
        return Page(
            lang=self.lang, path=self.path, kind="simple", status=404, noindex=True,
            title=f"{heading} — {self.content.studio_name}",
            body={
                "heading": heading,
                "intro": text(self.lang, f"{prefix}_text"),
                "link": (text(self.lang, "browse"), localize("/", self.lang)),
            },
        )


def build_page(request, pathname: str) -> Page:
    return PageBuilder(request, pathname).build()
