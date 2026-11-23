"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import SeoSettings


@register(SeoSettings)
class SeoSettingsTranslation(ShopTranslationOptions):
    fields = (
        "home_title", "home_description",
        "care_title", "care_description",
        "ingredients_title", "ingredients_description",
        "decorate_title", "decorate_description",
    )
