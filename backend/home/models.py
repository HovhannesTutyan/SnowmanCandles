from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from shop.models import validate_hex_color

LINK_HELP = "A slide links to either a candle or a collection (or nothing), not both."


class HeroSlide(models.Model):
    """One slide of the homepage carousel."""

    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to="slides/%Y/%m/",
        blank=True,
        help_text="Recommended size 1920x800. If empty, the linked item's image is used.",
    )
    button_text = models.CharField(max_length=40, blank=True, help_text='e.g. "Shop now"')
    candle = models.ForeignKey(
        "shop.Candle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hero_slides",
        help_text=LINK_HELP,
    )
    collection = models.ForeignKey(
        "shop.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hero_slides",
        help_text=LINK_HELP,
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Slide position; lower numbers come first."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.candle_id and self.collection_id:
            raise ValidationError(
                "Link the slide to a candle or a collection, not both.",
                code="both_links",
            )
        if not self.image and not self.linked_item:
            raise ValidationError(
                {"image": "Upload an image or link the slide to a candle or collection."},
                code="no_image",
            )

    @property
    def linked_item(self):
        return self.candle or self.collection

    @property
    def display_image(self):
        """The slide's own image, falling back to the linked item's image."""
        if self.image:
            return self.image
        item = self.linked_item
        if item and item.image:
            return item.image
        return None


CONTENT_IMAGE_FIELDS = [
    "made_before_image", "made_after_image", "video_image",
    "single_tile_image", "sets_tile_image",
    "custom_image_1", "custom_image_2",
]


def section_image(help_text=""):
    hint = "Optional. If empty, the image from the original design is used."
    return models.ImageField(
        upload_to="homepage/", blank=True, help_text=f"{help_text} {hint}".strip()
    )


class HomePageContent(models.Model):
    """Editable site texts and images (homepage, header, footer, product pages).
    There is only ever one row."""

    # Brand & contact
    studio_name = models.CharField(max_length=80, default="HugCrafts")
    accent_color = models.CharField(
        max_length=7,
        default="#B4451A",
        validators=[validate_hex_color],
        help_text="Colour of the main buttons and the logo flame.",
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        validators=[RegexValidator(r"^[A-Z]{3}$", "Use a 3-letter code like USD or EUR.")],
        help_text="3-letter currency code used to show prices (USD, EUR, AMD…).",
    )
    ticker_messages = models.TextField(
        default=(
            "Winter collection is here\n"
            "Order early for holiday delivery\n"
            "Every piece hand-painted\n"
            "Custom colours on request"
        ),
        help_text="Scrolling announcement bar at the top. One message per line.",
    )

    # Hero
    hero_eyebrow = models.CharField(
        max_length=120, default="Hand-cast · Hand-painted · Small batches"
    )
    hero_title = models.CharField(
        max_length=160, default="Little candles for the longest nights."
    )
    hero_text = models.TextField(
        default=(
            "Single candles and candle sets — each one cast in plaster, painted by hand "
            "and poured with wax, so no two are ever quite the same."
        )
    )
    hero_button_text = models.CharField(max_length=60, default="Shop the winter collection")
    hero_video_button_text = models.CharField(max_length=60, default="Watch how it's made")

    # Featured grid
    collection_eyebrow = models.CharField(max_length=80, default="The winter collection")
    collection_title = models.CharField(
        max_length=160, default="Painted for the season, made to stay out all year."
    )

    # How it's made
    made_title = models.CharField(max_length=120, default="Every piece starts out white.")
    made_text = models.TextField(
        default=(
            "Watch a plain plaster bauble become a painted candle — the same slow "
            "process behind every piece in the shop."
        )
    )
    made_before_image = section_image("Unpainted piece (shown first).")
    made_after_image = section_image(
        "The same piece painted, same size and position as the 'before' image."
    )
    step1_title = models.CharField(max_length=60, default="Cast")
    step1_text = models.CharField(
        max_length=255,
        default="Plaster is poured into the mould, set, then cleaned and smoothed by hand.",
    )
    step2_title = models.CharField(max_length=60, default="Paint")
    step2_text = models.CharField(
        max_length=255,
        default=(
            "Each leaf, dot and mitten is painted with a fine brush — slow work that "
            "makes every piece its own."
        ),
    )
    step3_title = models.CharField(max_length=60, default="Finish & pour")
    step3_text = models.CharField(
        max_length=255,
        default="Each piece is sealed, then filled with wax and a wick by hand.",
    )
    video_title = models.CharField(max_length=80, default="A day in the studio")
    video_caption = models.CharField(max_length=80, default="Studio video", blank=True)
    video_url = models.URLField(
        blank=True, help_text="Optional link (e.g. YouTube) opened by the video button."
    )
    video_image = section_image("Picture shown on the video button.")

    # Shop by type
    single_tile_text = models.CharField(
        "single candles tile text",
        max_length=120,
        default="One hand-painted piece, poured and ready to light",
    )
    single_tile_image = section_image()
    sets_tile_text = models.CharField(
        "candle sets tile text",
        max_length=120,
        default="Little winter scenes with a candle at their heart",
    )
    sets_tile_image = section_image()

    # Custom orders band
    custom_title = models.CharField(max_length=120, default="Want it in your colours?")
    custom_text = models.TextField(
        default=(
            "Pick a piece and tell us your palette, a name or a date — we'll paint it "
            "just for you. Perfect for weddings, teachers and first Christmases."
        )
    )
    custom_button_text = models.CharField(max_length=60, default="Request a custom piece")
    custom_image_1 = section_image()
    custom_image_2 = section_image()

    # Newsletter
    newsletter_title = models.CharField(max_length=120, default="Be first to see new pieces")
    newsletter_text = models.CharField(
        max_length=255,
        default="New designs come in small batches. Join the list for drops and studio news.",
    )

    # Footer
    footer_text = models.CharField(
        max_length=255, default="Hand-cast, hand-painted candles and candle sets."
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    instagram_handle = models.CharField(
        max_length=60, blank=True, help_text="Without the @, e.g. hugcrafts"
    )

    # Product pages (shared by every product)
    price_note = models.CharField(
        max_length=120,
        blank=True,
        default="Tax included. Free delivery in 1–2 days.",
        help_text="Small note next to the price.",
    )
    ships_in = models.CharField(
        max_length=40, blank=True, default="1–2 days", help_text='e.g. "1–2 days"'
    )
    care_text = models.TextField(
        "candle care",
        default=(
            "Trim the wick to about 5 mm before each use and burn on a heat-safe surface. "
            "Never leave a burning candle unattended, and keep it away from drafts, children "
            "and pets. Wipe the painted plaster with a soft, dry cloth."
        ),
    )
    shipping_text = models.TextField(
        "shipping & returns",
        default=(
            "Delivery is free and takes 1–2 days. Every piece is wrapped by hand, and as each "
            "candle is made by hand, please get in touch within 14 days if anything arrives "
            "damaged and we'll make it right."
        ),
    )
    # Basket & checkout
    delivery_text = models.CharField(
        max_length=120,
        default="Free delivery in 1–2 days",
        help_text="Shown in the basket and at checkout.",
    )
    order_success_text = models.TextField(
        "thank-you message",
        default=(
            "Thank you! We've received your order and will call you soon to confirm the "
            "details. Delivery is free and takes 1–2 days."
        ),
        help_text="Shown after a customer places an order.",
    )

    story_title = models.CharField(
        "making-of title",
        max_length=160,
        default="Hours of small brushstrokes in every one.",
        help_text="Used on product pages that have no making-of text of their own.",
    )
    story_text = models.TextField(
        "making-of text",
        default=(
            "Each piece is cast in plaster, painted by hand and filled with wax last. "
            "Because it's all done by hand, yours will have its own small differences — "
            "that's the charm."
        ),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "site content"
        verbose_name_plural = "site content"

    def __str__(self):
        return "Site content"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        if created:
            # Armenian and Russian versions of the default texts.
            from languages.catalog import fill_from_catalog
            from languages.conf import translated_fields

            if fill_from_catalog(obj, translated_fields(cls)):
                obj.save()
        return obj

    @property
    def ticker_list(self):
        return [line.strip() for line in self.ticker_messages.splitlines() if line.strip()]
