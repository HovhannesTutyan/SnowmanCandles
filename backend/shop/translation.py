"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import (
    Candle,
    CandleImage,
    CandleShowcaseView,
    Collection,
    CollectionImage,
    CollectionShowcaseView,
    Scent,
)

ITEM_FIELDS = ("title", "description", "burn_time", "size", "details", "story_title", "story_text")


@register(Scent)
class ScentTranslation(ShopTranslationOptions):
    fields = ("name",)


@register(Candle)
class CandleTranslation(ShopTranslationOptions):
    fields = ITEM_FIELDS


@register(Collection)
class CollectionTranslation(ShopTranslationOptions):
    fields = ITEM_FIELDS


@register(CandleImage)
@register(CollectionImage)
class GalleryImageTranslation(ShopTranslationOptions):
    fields = ("label",)


@register(CandleShowcaseView)
@register(CollectionShowcaseView)
class ShowcaseViewTranslation(ShopTranslationOptions):
    fields = ("label", "short_label", "caption")
