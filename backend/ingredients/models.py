from django.db import models

from shop.models import validate_hex_color

PHOTO_HELP = "Optional photo. If empty, the drawn illustration from the design is shown."


class IngredientsPage(models.Model):
    """Hero and closing texts of the "What's inside our candles" page. Only ever one row."""

    nav_title = models.CharField(
        max_length=40, default="Ingredients", help_text="Title in the bottom chapter bar."
    )
    hero_eyebrow = models.CharField(max_length=60, default="Ingredients")
    hero_title = models.CharField(max_length=120, default="What's inside our candles")
    hero_text = models.TextField(
        default=(
            "Five honest things — soy wax, a hand-cast plaster vessel, a wick, a careful "
            "measure of fragrance and a little colour — and nothing we wouldn't happily explain."
        )
    )
    hero_link_text = models.CharField(
        max_length=60,
        default="Start with the wax",
        blank=True,
        help_text="Link that scrolls to the first chapter. Leave empty to hide it.",
    )
    hero_image = models.ImageField(upload_to="ingredients/", blank=True, help_text=PHOTO_HELP)
    hero_image_label = models.CharField(
        max_length=60, blank=True, default="Raw plaster, before painting",
        help_text="Small label on the hero picture.",
    )

    cta_title = models.CharField(
        "closing title", max_length=120, default="Made by hand, made to last"
    )
    cta_text = models.CharField(
        "closing text",
        max_length=255,
        default="Soy to burn, plaster to keep. Find the piece that feels like home.",
    )
    cta_button_text = models.CharField(
        "closing button", max_length=40, default="Shop Candles"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ingredients page"
        verbose_name_plural = "ingredients page"

    def __str__(self):
        return "Ingredients page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Chapter(models.Model):
    """One ingredient chapter: a big banner, then text, points, questions, cards and swatches."""

    class Illustration(models.TextChoices):
        SOY = "soy", "Soy wax (creamy wax and flakes)"
        PLASTER = "plaster", "Plaster (textured surface with a vessel)"
        WICK = "wick", "Wick (lit candle in the dark)"
        FRAGRANCE = "fragrance", "Fragrance (botanical sprigs)"
        COLOUR = "colour", "Colour (stripes from this chapter's swatches)"
        NONE = "none", "None (plain banner colour)"

    class TextTone(models.TextChoices):
        DARK = "dark", "Dark text (for light banners)"
        LIGHT = "light", "Light text (for dark banners)"

    anchor = models.SlugField(
        max_length=40,
        unique=True,
        help_text='Used in the page address, e.g. "soy" makes /ingredients#soy.',
    )
    nav_label = models.CharField(
        max_length=30, help_text='Short name in the bottom chapter bar, e.g. "Soy Wax".'
    )
    title = models.CharField(max_length=60, help_text="The big banner title.")
    intro = models.TextField(help_text="Short text on the banner.")
    body = models.TextField(
        blank=True, help_text="Main text. Leave an empty line between paragraphs."
    )
    illustration = models.CharField(
        max_length=20, choices=Illustration.choices, default=Illustration.NONE
    )
    banner_image = models.ImageField(
        upload_to="ingredients/", blank=True, help_text=f"Wide photo. {PHOTO_HELP}"
    )
    banner_color = models.CharField(
        max_length=7,
        default="#EFE3CC",
        validators=[validate_hex_color],
        help_text="Banner background (shown around the illustration and on phones).",
    )
    banner_text = models.CharField(
        "banner text colour", max_length=10, choices=TextTone.choices, default=TextTone.DARK
    )
    cards_title = models.CharField(
        max_length=80, blank=True, help_text='Heading above the cards, e.g. "About our wicks".'
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers come first.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide this chapter.")

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def paragraphs(self):
        return [p.strip() for p in self.body.replace("\r\n", "\n").split("\n\n") if p.strip()]


class ChapterItem(models.Model):
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class ChapterPoint(ChapterItem):
    """A bullet point: a bold lead-in followed by text."""

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="points")
    lead = models.CharField(max_length=80, help_text='Bold start, e.g. "Renewable".')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.lead


class ChapterQuestion(ChapterItem):
    """An expandable question on the right of the chapter text."""

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return self.question


class ChapterCard(ChapterItem):
    class Icon(models.TextChoices):
        BRAID = "braid", "Braid (cotton wick)"
        WOOD = "wood", "Wooden wick"
        CLOCK = "clock", "Clock"
        SCISSORS = "scissors", "Scissors"
        LEAF = "leaf", "Leaf"
        DROP = "drop", "Drop"

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="cards")
    icon = models.CharField(max_length=20, choices=Icon.choices, default=Icon.LEAF)
    title = models.CharField(max_length=60)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ChapterSwatch(ChapterItem):
    """A colour circle with a name and a short note (e.g. the scent it goes with)."""

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="swatches")
    name = models.CharField(max_length=40)
    color = models.CharField(max_length=7, validators=[validate_hex_color])
    note = models.CharField(max_length=60, blank=True)

    class Meta(ChapterItem.Meta):
        verbose_name_plural = "swatches"

    def __str__(self):
        return self.name
