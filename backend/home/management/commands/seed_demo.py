from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from care.models import CarePage
from decorate.models import DecoratePage, GalleryImage
from home.models import HeroSlide, HomePageContent
from languages.catalog import fill_all_from_catalog
from shop.models import Candle, CandleShowcaseView, ProductType, Scent

DEMO_IMAGES = Path(__file__).resolve().parents[2] / "demo_images"

# The six pieces from the homepage design. Every piece is a candle: a set has more than
# one piece (the campfire is the candle, the snowmen are plaster). Prices are placeholders.
DEMO_PRODUCTS = [
    {
        "title": "Snowmen by the Campfire",
        "product_type": ProductType.SET,
        "tint": "#E4ECDC",
        "image": "snowmen-campfire.webp",
        "price": "34.00",
        "description": "Two plaster snowmen in knitted hats warm their mittens by a campfire "
        "candle. Light the logs for a cosy glow on the mantel.",
    },
    {
        "title": "Vintage Roadster Candle",
        "product_type": ProductType.CANDLE,
        "tint": "#F3E1DB",
        "image": "vintage-roadster-candle.webp",
        "price": "28.00",
        "description": "A classic red roadster with golden wheels, its cab filled with "
        "candle wax.",
    },
    {
        "title": "Carousel Candle",
        "product_type": ProductType.CANDLE,
        "tint": "#EFE5D8",
        "image": "carousel-candle.webp",
        "price": "42.00",
        "description": "Galloping horses in warm bronze and gold around a hidden candle, "
        "with a lid shaped like the carousel roof.",
    },
    {
        "title": "Holly Bauble Candle",
        "product_type": ProductType.CANDLE,
        "tint": "#E4ECDC",
        "image": "holly-bauble-candle.webp",
        "price": "24.00",
        "description": "A bauble candle with a lid, hand-painted holly and a ring of gold dots.",
    },
    {
        "title": "Pine Garland Bauble Candle",
        "product_type": ProductType.CANDLE,
        "tint": "#EAE8DE",
        "image": "pine-garland-bauble.webp",
        "price": "24.00",
        "description": "Little green pines strung with dotted gold garlands, top to bottom, "
        "around a poured candle.",
    },
    {
        "title": "Christmas Tree Candle",
        "product_type": ProductType.CANDLE,
        "tint": "#E4ECDC",
        "image": "christmas-tree-candle.webp",
        "price": "18.00",
        "description": "A bright green tree candle with golden baubles and a white star on top.",
    },
]

# The first four pieces rotate on the hero pedestal, as in the design.
HERO_SLIDE_COUNT = 4

# Decorate page gallery, from the design: (file, caption, description, candles shown).
ROADSTER, CAROUSEL, HOLLY = "Vintage Roadster Candle", "Carousel Candle", "Holly Bauble Candle"
PINE, TREE, SNOWMEN = "Pine Garland Bauble Candle", "Christmas Tree Candle", "Snowmen by the Campfire"
DEMO_GALLERY = [
    ("01-evening-table.webp", "Roadster Candle on a walnut table",
     "A red painted roadster candle glowing on a dark walnut table with soy pillar candles",
     [ROADSTER]),
    ("02-linen-shelf.webp", "Carousel Candle + Holly Bauble on a linen shelf",
     "A bronze carousel candle and a holly bauble candle on a pale shelf in soft daylight",
     [CAROUSEL, HOLLY]),
    ("03-mantel.webp", "Snowmen by the Campfire with a Christmas Tree Candle",
     "The snowmen campfire set and a green painted tree candle on a mantel lit by pillar candles",
     [SNOWMEN, TREE]),
    ("04-bedside.webp", "Ivory plaster bauble by the bed",
     "An unpainted ivory plaster bauble beside a single lit soy candle on a bedside table", []),
    ("05-plaster-tray.webp", "Plaster tray + three soy pillars",
     "Three lit soy pillar candles of different heights on a plaster tray", []),
    ("06-window-sill.webp", "Two bauble candles on a stone sill",
     "Pine garland and holly bauble candles on a pale stone window sill in daylight",
     [PINE, HOLLY]),
    ("07-dining.webp", "Roadster centrepiece with taper candles",
     "Red roadster candle as a dining centrepiece between two tall lit taper candles", [ROADSTER]),
    ("08-console.webp", "Carousel Candle on the hallway console",
     "Bronze carousel candle on a stone console with dried grasses", [CAROUSEL]),
    ("09-bath.webp", "Ivory plaster bauble for cotton pads, soy candle beside",
     "Ivory plaster bauble and a lit soy candle on a pale stone bathroom ledge", []),
    ("10-terrace.webp", "Snowmen on the terrace table at dusk",
     "The snowmen campfire set on an outdoor table at dusk with warm lights behind", [SNOWMEN]),
    ("11-heights.webp", "Grouping heights: carousel, roadster, bauble",
     "Carousel, roadster and pine bauble candles grouped at different heights",
     [CAROUSEL, ROADSTER, PINE]),
    ("12-holly-close.webp", "Holly Bauble Candle, up close",
     "Close view of a white bauble candle hand-painted with green holly", [HOLLY]),
    ("13-tree-evening.webp", "Christmas Tree + Pine Bauble by candlelight",
     "Green painted tree candle and pine garland bauble candle beside a lit soy candle in the evening",
     [TREE, PINE]),
    ("14-roadster-day.webp", "Roadster Candle in morning light",
     "Red roadster candle on a light oak desk in morning daylight", [ROADSTER]),
    ("15-snowmen-glow.webp", "Snowmen by the Campfire, evening glow",
     "The snowmen campfire set glowing in warm evening light", [SNOWMEN]),
    ("16-dusk-trio.webp", "Soy pillars at dusk on the terrace",
     "Three lit soy pillar candles on a plaster tray outdoors at dusk", []),
]
# Room card title -> gallery picture it opens.
DEMO_ROOM_PICTURES = {
    "Living room": "02-linen-shelf.webp",
    "Bedroom": "04-bedside.webp",
    "Bathroom": "09-bath.webp",
    "Dining table": "05-plaster-tray.webp",
    "Entryway": "08-console.webp",
    "Terrace & garden": "16-dusk-trio.webp",
}

# Product showcases: product title -> folder in demo_images/showcase/ and its views
# (file, label, button text, caption, ring colour, background colour, view type).
DEMO_SHOWCASES = {
    "Snowmen by the Campfire": ("snowmen-by-the-campfire", [
        ("front.webp", "Front", "Front", "Two hand-painted snowmen warming up by the fire.",
         "#7FB045", "#EEF3E6", "side"),
        ("three-quarter.webp", "Three-quarter", "Angle", "Knitted-texture hat, scarf and mittens.",
         "#E8743B", "#F6ECE4", "side"),
        ("back.webp", "Back", "Back", "Fully sculpted all the way round.",
         "#6FA8DC", "#E9F0F6", "side"),
        ("side.webp", "Fireside", "Side", "The little campfire with stone ring.",
         "#A58AD6", "#EFEBF6", "side"),
        ("top.webp", "From above", "Top", "Snowy base with the fire pit in the middle.",
         "#E9A23B", "#F6EFE2", "top"),
        ("bottom.webp", "Underneath", "Bottom", "Smooth flat base — sits steady on any shelf.",
         "#E07A8A", "#F5EAEC", "bottom"),
    ]),
}

# Shown as a "name · price" label on the care page's fragrance picture.
CARE_PAGE_CANDLE = "Holly Bauble Candle"

# Example scents; replace them under Shop -> Scents.
DEMO_SCENTS = ["Unscented", "Pine & cedar", "Cinnamon & orange"]

# Product page details. Burn times and sizes are placeholders: replace them in the admin.
DEMO_PAGE_DETAILS = {
    "Snowmen by the Campfire": {
        "burn_time": "~15 hours",
        "size": "16 × 12 × 11 cm",
        "details": "Hand-cast plaster snowmen and base, painted by hand. The campfire logs "
        "are the candle, poured in soy wax with a cotton wick.",
    },
    "Vintage Roadster Candle": {
        "burn_time": "~25 hours",
        "size": "14 × 7 × 8 cm",
        "details": "Hand-cast plaster holder, painted by hand in red, gold and black. "
        "Filled with soy wax and a cotton wick.",
        "story_title": "Hours of small brushstrokes in every one.",
        "story_text": "The body is shaded red by hand, the wheels and grille picked out in "
        "gold, and the candle poured into the cab last. Because it's all done by hand, "
        "yours will have its own small differences — that's the charm.",
        # Wick position from the product page design.
        "flame_x": Decimal("47.6"),
        "flame_y": Decimal("86.5"),
    },
    "Carousel Candle": {
        "burn_time": "~30 hours",
        "size": "10 × 10 × 13 cm",
        "details": "Hand-cast plaster carousel with a lift-off roof, painted in bronze and "
        "gold. Filled with soy wax and a cotton wick.",
    },
    "Holly Bauble Candle": {
        "burn_time": "~20 hours",
        "size": "9 × 9 × 10 cm",
        "details": "Hand-cast plaster bauble with a lid, painted with holly and gold dots. "
        "Filled with soy wax and a cotton wick.",
    },
    "Pine Garland Bauble Candle": {
        "burn_time": "~20 hours",
        "size": "9 × 9 × 10 cm",
        "details": "Hand-cast plaster bauble with a lid, painted with pines and gold garlands. "
        "Filled with soy wax and a cotton wick.",
    },
    "Christmas Tree Candle": {
        "burn_time": "~12 hours",
        "size": "7 × 6 × 9 cm",
        "details": "A tree-shaped candle, hand-painted with golden baubles and a white star.",
    },
}


class Command(BaseCommand):
    help = (
        "Load the products and hero slides from the homepage design so the site has "
        "something to show. Safe to run more than once: existing items are only "
        "filled in where a product page field is still empty."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        HomePageContent.load()
        scents = [
            Scent.objects.get_or_create(name=name, defaults={"order": order})[0]
            for order, name in enumerate(DEMO_SCENTS)
        ]

        candles = []
        for order, data in enumerate(DEMO_PRODUCTS, start=1):
            candle = Candle.objects.filter(title=data["title"]).first()
            if candle:
                self.stdout.write(f"  exists   {candle.title}")
            else:
                candle = Candle(
                    title=data["title"],
                    product_type=data["product_type"],
                    tint=data["tint"],
                    price=Decimal(data["price"]),
                    description=data["description"],
                    stock=10,
                    is_featured=True,
                    featured_order=order,
                )
                with open(DEMO_IMAGES / data["image"], "rb") as fh:
                    candle.image.save(data["image"], File(fh), save=False)
                candle.full_clean()
                candle.save()
                self.stdout.write(self.style.SUCCESS(f"  created  {candle.title}"))
            self._fill_page_details(candle, scents)
            self._seed_showcase(candle)
            candles.append(candle)

        if HeroSlide.objects.exists():
            self.stdout.write("  hero slides already exist, skipped")
        else:
            for order, candle in enumerate(candles[:HERO_SLIDE_COUNT], start=1):
                HeroSlide.objects.create(title=candle.title, candle=candle, order=order)
            self.stdout.write(self.style.SUCCESS(f"  created  {HERO_SLIDE_COUNT} hero slides"))

        care_page = CarePage.load()
        if care_page.fragrance_product is None:
            care_page.fragrance_product = Candle.objects.filter(title=CARE_PAGE_CANDLE).first()
            care_page.save(update_fields=["fragrance_product", "updated_at"])

        self._seed_decorate_gallery()
        self._seed_decorate_video()

        # Armenian and Russian versions of the demo texts (empty translations only).
        filled = fill_all_from_catalog()
        if filled:
            self.stdout.write(self.style.SUCCESS(f"  translated {filled} item(s) into Armenian and Russian"))

        self.stdout.write(self.style.SUCCESS("Demo content ready."))

    def _fill_page_details(self, candle, scents):
        """Fill product page fields that are still empty; never overwrite admin edits."""
        changed = []
        for field, value in DEMO_PAGE_DETAILS.get(candle.title, {}).items():
            if getattr(candle, field) in ("", None):
                setattr(candle, field, value)
                changed.append(field)
        if changed:
            candle.full_clean()
            candle.save(update_fields=[*changed, "updated_at"])
        if not candle.scents.exists():
            candle.scents.set(scents)

    def _seed_decorate_gallery(self):
        """Upload the design's gallery pictures once and link the room cards to them."""
        if GalleryImage.objects.exists():
            self.stdout.write("  decorate gallery already exists, skipped")
            return

        by_file = {}
        for order, (filename, caption, alt, titles) in enumerate(DEMO_GALLERY, start=1):
            picture = GalleryImage(caption=caption, alt=alt, order=order)
            with open(DEMO_IMAGES / "decorate" / filename, "rb") as fh:
                picture.image.save(filename, File(fh), save=False)
            picture.save()
            picture.products.set(Candle.objects.filter(title__in=titles))
            by_file[filename] = picture

        for room in DecoratePage.load().rooms.filter(picture__isnull=True):
            filename = DEMO_ROOM_PICTURES.get(room.title)
            if filename:
                room.picture = by_file[filename]
                room.save(update_fields=["picture"])
        self.stdout.write(self.style.SUCCESS(f"  created  {len(DEMO_GALLERY)} gallery pictures"))

    def _seed_decorate_video(self):
        """The decorate page hero video (and its first frame as the picture), if none yet."""
        page = DecoratePage.load()
        if page.hero_video:
            return
        with open(DEMO_IMAGES / "decorate" / "hero-video.mp4", "rb") as fh:
            page.hero_video.save("hero-video.mp4", File(fh), save=False)
        if not page.hero_image:
            with open(DEMO_IMAGES / "decorate" / "hero-video-poster.jpg", "rb") as fh:
                page.hero_image.save("hero-video-poster.jpg", File(fh), save=False)
        page.save()
        self.stdout.write(self.style.SUCCESS("  added    decorate page hero video"))

    def _seed_showcase(self, candle):
        """Add the demo showcase views to a product that has none yet."""
        if candle.title not in DEMO_SHOWCASES or candle.showcase_views.exists():
            return
        folder, views = DEMO_SHOWCASES[candle.title]
        for order, (filename, label, short, caption, color, tint, group) in enumerate(views, start=1):
            view = CandleShowcaseView(
                candle=candle, label=label, short_label=short, caption=caption,
                color=color, tint=tint, group=group, order=order,
            )
            with open(DEMO_IMAGES / "showcase" / folder / filename, "rb") as fh:
                view.image.save(f"{folder}-{filename}", File(fh), save=False)
            view.save()
        self.stdout.write(self.style.SUCCESS(f"  added    showcase to {candle.title}"))
