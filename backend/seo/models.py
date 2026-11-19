from django.core.validators import RegexValidator
from django.db import models

TITLE_HELP = "Shown as the link in Google results and on browser tabs. About 60 characters. Leave empty to use the text shown in grey."
DESCRIPTION_HELP = "Shown under the link in Google results. About 150 characters. Leave empty to use the text shown in grey."


def seo_title(verbose_name="search title"):
    return models.CharField(verbose_name, max_length=120, blank=True, help_text=TITLE_HELP)


def seo_description(verbose_name="search description"):
    return models.TextField(verbose_name, max_length=320, blank=True, help_text=DESCRIPTION_HELP)


class SeoSettings(models.Model):
    """How the site's pages appear in Google and in shared links (a single row).

    Product pages have their own search title and description on each product.
    """

    home_title = seo_title("home page: search title")
    home_description = seo_description("home page: search description")
    care_title = seo_title("candle care page: search title")
    care_description = seo_description("candle care page: search description")
    ingredients_title = seo_title("ingredients page: search title")
    ingredients_description = seo_description("ingredients page: search description")
    decorate_title = seo_title("decorate page: search title")
    decorate_description = seo_description("decorate page: search description")

    share_image = models.ImageField(
        "preview image for shared links",
        upload_to="seo/",
        blank=True,
        help_text="Shown when a page link is shared on Telegram, WhatsApp, Facebook… "
        "1200 × 630 px works best. Product pages use the product photo instead. "
        "Leave empty to use the first featured product's photo.",
    )

    delivery_country = models.CharField(
        max_length=2,
        default="AM",
        validators=[RegexValidator(r"^[A-Z]{2}$", "Use a two-letter country code, e.g. AM.")],
        help_text="Where you deliver, as a two-letter code (AM = Armenia). Tells Google "
        "where the free delivery applies.",
    )
    delivery_days_min = models.PositiveSmallIntegerField("delivery takes at least (days)", default=1)
    delivery_days_max = models.PositiveSmallIntegerField("delivery takes at most (days)", default=2)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "search engine settings"
        verbose_name_plural = "search engine settings"

    def __str__(self):
        return "Search engine settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
