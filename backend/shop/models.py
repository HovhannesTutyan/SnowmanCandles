from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify

LOW_STOCK_THRESHOLD = 5
DEFAULT_TINT = "#E4ECDC"

validate_hex_color = RegexValidator(
    r"^#[0-9A-Fa-f]{6}$", "Enter a colour like #E4ECDC.", code="invalid_color"
)


class ProductType(models.TextChoices):
    CANDLE = "candle", "Single candle"
    SET = "set", "Candle set"


class Scent(models.Model):
    """A scent a candle can be ordered in, e.g. "Unscented" or "Pine & cedar"."""

    name = models.CharField(max_length=60, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are listed first.")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


PERCENT_VALIDATORS = [MinValueValidator(0), MaxValueValidator(100)]


def validate_positive_price(value):
    if value is None or value <= Decimal("0"):
        raise ValidationError("Price must be greater than 0.", code="non_positive_price")


class BaseItem(models.Model):
    """Fields and behaviour shared by every sellable item."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Leave blank to generate it automatically from the title.",
    )
    description = models.TextField()
    image = models.ImageField()  # upload_to is set on each concrete model
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[validate_positive_price]
    )
    stock = models.PositiveIntegerField(default=0, help_text="Number of units in stock.")
    tint = models.CharField(
        "card colour",
        max_length=7,
        default=DEFAULT_TINT,
        validators=[validate_hex_color],
        help_text="Background colour behind the image on product cards.",
    )
    is_featured = models.BooleanField(
        default=False, help_text="Show this item in the homepage featured section."
    )
    featured_order = models.PositiveIntegerField(
        default=0, help_text="Position in the featured section; lower numbers come first."
    )

    # Product page
    scents = models.ManyToManyField(
        Scent,
        blank=True,
        related_name="%(class)ss",
        help_text="Scents offered on the product page. The first one is selected by default.",
    )
    burn_time = models.CharField(max_length=40, blank=True, help_text='e.g. "~25 hours"')
    size = models.CharField(max_length=60, blank=True, help_text='e.g. "14 × 7 × 8 cm"')
    details = models.TextField(
        blank=True, help_text="Materials, wax, wick, weight… Shown under “Details”."
    )
    story_title = models.CharField(
        "making-of title",
        max_length=160,
        blank=True,
        help_text="Optional. If empty, the shared text from Site content is used.",
    )
    story_text = models.TextField(
        "making-of text",
        blank=True,
        help_text="Optional. How this piece is made. If empty, the shared text is used.",
    )
    flame_x = models.DecimalField(
        "wick position, % from left",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
    )
    flame_y = models.DecimalField(
        "wick position, % from bottom",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=PERCENT_VALIDATORS,
        help_text="Set both to show a “Lit” view with an animated flame on the wick. "
        "Measured on the main image: 0 = left/bottom edge, 100 = right/top edge.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="%(app_label)s_%(class)s_price_gt_0",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.stock > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock <= LOW_STOCK_THRESHOLD

    @property
    def flame(self):
        """Wick position as {"x": %, "y": %}, or None when no lit view is set up."""
        if self.flame_x is None or self.flame_y is None:
            return None
        return {"x": float(self.flame_x), "y": float(self.flame_y)}

    def clean(self):
        super().clean()
        if (self.flame_x is None) != (self.flame_y is None):
            raise ValidationError(
                {"flame_y": "Set both wick positions, or leave both empty."},
                code="incomplete_flame",
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        max_length = self._meta.get_field("slug").max_length
        base = slugify(self.title)[: max_length - 10].strip("-") or "item"
        siblings = type(self)._default_manager.exclude(pk=self.pk)

        slug, counter = base, 2
        while siblings.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug


class Candle(BaseItem):
    """A product sold on its own: a single candle or a candle set."""

    image = models.ImageField(
        upload_to="candles/%Y/%m/",
        help_text="Tip: a cut-out image with a transparent background looks best on the homepage.",
    )
    product_type = models.CharField(
        "type",
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.CANDLE,
        db_index=True,
        help_text="Single candle: one piece (e.g. the roadster). Candle set: more than one "
        "piece, e.g. a wood candle with plaster snowmen around it.",
    )


class Collection(BaseItem):
    image = models.ImageField(upload_to="collections/%Y/%m/")
    candles = models.ManyToManyField(
        Candle,
        blank=True,
        related_name="collections",
        help_text="Candles included in this collection (display only; "
        "the collection has its own price and stock).",
    )


class BaseGalleryImage(models.Model):
    """An extra photo on a product page (close-ups, lit photos…)."""

    label = models.CharField(
        max_length=60, help_text='Short name under the photo, e.g. "Wheel detail".'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class CandleImage(BaseGalleryImage):
    candle = models.ForeignKey(Candle, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="candles/gallery/%Y/%m/")


class CollectionImage(BaseGalleryImage):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="collections/gallery/%Y/%m/")


class BaseShowcaseView(models.Model):
    """One view in a product page's animated showcase (the glow-pedestal viewer)."""

    class Group(models.TextChoices):
        SIDE = "side", "Side view"
        TOP = "top", "From above"
        BOTTOM = "bottom", "Underneath"

    label = models.CharField(max_length=40, help_text='Big text, e.g. "Three-quarter".')
    short_label = models.CharField(
        "button text",
        max_length=20,
        blank=True,
        help_text='Text on the small button, e.g. "Angle". Empty: uses the label.',
    )
    caption = models.CharField(max_length=160, blank=True)
    color = models.CharField(
        "ring colour",
        max_length=7,
        default="#7FB045",
        validators=[validate_hex_color],
        help_text="The glowing ring.",
    )
    tint = models.CharField(
        "background colour",
        max_length=7,
        default="#EEF3E6",
        validators=[validate_hex_color],
        help_text="The scene behind the product while this view is showing.",
    )
    group = models.CharField(
        "view type",
        max_length=10,
        choices=Group.choices,
        default=Group.SIDE,
        help_text="Swiping down or up (and the up/down keys) jumps to the From above / Underneath view.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class CandleShowcaseView(BaseShowcaseView):
    candle = models.ForeignKey(Candle, on_delete=models.CASCADE, related_name="showcase_views")
    image = models.ImageField(
        upload_to="showcase/%Y/%m/",
        help_text="A cut-out with a transparent background, product at the bottom of the image.",
    )


class CollectionShowcaseView(BaseShowcaseView):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="showcase_views"
    )
    image = models.ImageField(
        upload_to="showcase/%Y/%m/",
        help_text="A cut-out with a transparent background, product at the bottom of the image.",
    )
