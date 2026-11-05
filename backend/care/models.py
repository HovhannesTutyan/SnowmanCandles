from django.db import models

PHOTO_HELP = (
    "Optional photo. If empty, the page shows the candlelit scene from the design, "
    "made from product cut-outs."
)


class CarePage(models.Model):
    """The "Candle care & tips" page. There is only ever one row; its lists are inlines."""

    # Hero
    hero_title = models.CharField(
        max_length=120,
        default="The art of a\nperfect burn",
        help_text="Press Enter to choose where the line breaks.",
    )
    hero_text = models.TextField(
        default=(
            "Every piece we make is cast and painted by hand, slowly. A little care in return "
            "keeps the flame clean, the wax even and your painted holder beautiful long after "
            "the last glow. Here's everything we've learned at the studio."
        )
    )
    hero_image = models.ImageField(
        upload_to="care/", blank=True, help_text=f"Wide photo, about 16:7. {PHOTO_HELP}"
    )

    # Section headings
    tips_eyebrow = models.CharField(
        "tips heading", max_length=120, default="Four habits for a better burn"
    )
    rituals_title = models.CharField(
        "care rituals heading",
        max_length=160,
        default="Little rituals that keep your candles beautiful",
    )

    # Fragrance section
    fragrance_eyebrow = models.CharField(max_length=80, default="Fragrance & afterlife")
    fragrance_title = models.CharField(max_length=160, default="Make every hour of scent count")
    fragrance_text = models.TextField(
        default=(
            "Fragrance lives in the melt pool, so the way you burn shapes how a room smells. "
            "And when the wax is gone, the piece itself is only getting started."
        )
    )
    fragrance_image = models.ImageField(
        upload_to="care/", blank=True, help_text=f"Portrait photo, about 1:1. {PHOTO_HELP}"
    )
    fragrance_product = models.ForeignKey(
        "shop.Candle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured candle",
        help_text="Optional. Shown as a “name · price” label on the fragrance picture, "
        "linking to its product page.",
    )

    faq_title = models.CharField("FAQ heading", max_length=40, default="F.A.Q.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "candle care page"
        verbose_name_plural = "candle care page"

    def __str__(self):
        return "Candle care page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CarePageItem(models.Model):
    page = models.ForeignKey(CarePage, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class CareTip(CarePageItem):
    """A numbered tip ("01 Let the first burn go wide")."""

    page = models.ForeignKey(CarePage, on_delete=models.CASCADE, related_name="tips")
    title = models.CharField(max_length=120)
    text = models.TextField()

    def __str__(self):
        return self.title


class CareRitual(CarePageItem):
    """An item in the "Little rituals" list."""

    page = models.ForeignKey(CarePage, on_delete=models.CASCADE, related_name="rituals")
    title = models.CharField(max_length=120)
    text = models.TextField()

    def __str__(self):
        return self.title


class FragranceTip(CarePageItem):
    """A point in the fragrance section: a bold lead-in followed by text."""

    page = models.ForeignKey(CarePage, on_delete=models.CASCADE, related_name="fragrance_tips")
    lead = models.CharField(max_length=120, help_text='Bold start, e.g. "Give it time to bloom."')
    text = models.TextField()

    def __str__(self):
        return self.lead


class FAQ(CarePageItem):
    page = models.ForeignKey(CarePage, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=200)
    answer = models.TextField()

    class Meta(CarePageItem.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
