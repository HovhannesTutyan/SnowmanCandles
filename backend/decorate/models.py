from django.db import models

DESIGN_IMAGE_HELP = "Optional. If empty, the picture from the original design is used."
BOLD_HELP = (
    "Leave an empty line between paragraphs. Wrap words in **double asterisks** to make "
    "them bold."
)


class DecoratePage(models.Model):
    """Texts and pictures of the "Decorate with candles" page. Only ever one row.

    The room cards are edited inline on this page; gallery pictures have their own list.
    """

    # Hero
    hero_eyebrow = models.CharField(max_length=60, default="Styling & Décor")
    hero_title = models.CharField(
        max_length=120,
        default="Decorate\nwith light",
        help_text="Press Enter to choose where the line breaks.",
    )
    hero_text = models.TextField(
        default=(
            "Ideas for styling soy candles and hand-cast plaster pieces in every room — from a "
            "quiet bedside to a table set for friends."
        )
    )
    hero_link_text = models.CharField(
        max_length=60,
        blank=True,
        default="Browse the gallery",
        help_text="Link that scrolls to the gallery. Leave empty to hide it.",
    )
    hero_image = models.ImageField(
        upload_to="decorate/", blank=True, help_text=f"Tall picture (about 3:4). {DESIGN_IMAGE_HELP}"
    )
    hero_image_alt = models.CharField(
        "hero picture description",
        max_length=255,
        blank=True,
        default=(
            "A styled oak shelf with a carousel candle, a holly bauble candle, a lit roadster "
            "candle, a soy pillar candle and dried grasses in a plaster vase"
        ),
        help_text="Describes the picture for screen readers and search engines.",
    )

    # Story
    story_title = models.CharField(
        max_length=160, default="A home feels finished with candlelight"
    )
    story_subtitle = models.CharField(
        max_length=200,
        blank=True,
        default="A few small flames, placed with intention, change a whole room.",
    )
    story_text = models.TextField(
        blank=True,
        help_text=BOLD_HELP,
        default=(
            "Start in the **living room**, where a low tray of soy pillars on the coffee table "
            "becomes the room's heartbeat. In the **bedroom**, keep it calm — one candle and one "
            "plaster piece on the nightstand, with soft lavender or cedar notes. A small plaster "
            "bauble on the **bathroom** ledge holds cotton pads by day and sits beside a gentle "
            "flame at bath time.\n\n"
            "On the **dining table**, **group different heights** — a tall taper, a squat "
            "pillar, a painted piece — so light falls at every level, and choose unscented "
            "candles so nothing competes with dinner. Welcome guests with a plaster dish for keys "
            "in the **entryway**, and on the **terrace**, gather candles on a tray, sheltered "
            "from the breeze. **Pair soy candles with plaster trays, holders and objects**, and "
            "pick a **scent for each room**."
        ),
    )

    # Gallery heading
    gallery_title = models.CharField(max_length=60, default="Gallery")
    gallery_text = models.CharField(
        max_length=200,
        blank=True,
        default="Drag, swipe or use the arrows. Tap any picture to see it full size.",
    )

    # Closing call to action
    cta_title = models.CharField("closing title", max_length=120, default="Bring the look home")
    cta_text = models.CharField(
        "closing text",
        max_length=255,
        default="Every candle in these pictures is made by hand in our studio.",
    )
    cta_button_text = models.CharField("closing button", max_length=40, default="Shop Candles")
    cta_image = models.ImageField(
        "closing picture", upload_to="decorate/", blank=True, help_text=DESIGN_IMAGE_HELP
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "decorate page"
        verbose_name_plural = "decorate page"

    def __str__(self):
        return "Decorate page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryImage(models.Model):
    """A square picture in the gallery slider (and the full-screen viewer)."""

    image = models.ImageField(
        upload_to="decorate/gallery/", help_text="Square works best, about 1200 × 1200 px."
    )
    caption = models.CharField(max_length=120, help_text="Shown on the picture and in the viewer.")
    alt = models.CharField(
        "description",
        max_length=255,
        help_text="Describes the picture for screen readers and search engines.",
    )
    products = models.ManyToManyField(
        "shop.Candle",
        blank=True,
        related_name="decorate_images",
        verbose_name="candles in this picture",
        help_text="Shown as “In this picture” links in the full-screen viewer.",
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers come first.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide this picture.")

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption


class Room(models.Model):
    """A room card under the story ("Living room", "Bedroom", …)."""

    page = models.ForeignKey(DecoratePage, on_delete=models.CASCADE, related_name="rooms")
    title = models.CharField(max_length=40)
    text = models.CharField(max_length=160)
    picture = models.ForeignKey(
        GalleryImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="A gallery picture. Clicking the card opens it in the full-screen viewer.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
