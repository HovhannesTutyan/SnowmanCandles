"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import DecoratePage, GalleryImage, Room


@register(DecoratePage)
class DecoratePageTranslation(ShopTranslationOptions):
    fields = (
        "hero_eyebrow", "hero_title", "hero_text", "hero_link_text", "hero_image_alt",
        "story_title", "story_subtitle", "story_text",
        "gallery_title", "gallery_text",
        "cta_title", "cta_text", "cta_button_text",
    )


@register(GalleryImage)
class GalleryImageTranslation(ShopTranslationOptions):
    fields = ("caption", "alt")


@register(Room)
class RoomTranslation(ShopTranslationOptions):
    fields = ("title", "text")
