"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import HeroSlide, HomePageContent


@register(HeroSlide)
class HeroSlideTranslation(ShopTranslationOptions):
    fields = ("title", "subtitle", "button_text")


@register(HomePageContent)
class HomePageContentTranslation(ShopTranslationOptions):
    # Not translated: the studio name (a brand), colours, currency, contact details, links.
    fields = (
        "ticker_messages",
        "hero_eyebrow", "hero_title", "hero_text", "hero_button_text", "hero_video_button_text",
        "collection_eyebrow", "collection_title",
        "made_title", "made_text",
        "step1_title", "step1_text", "step2_title", "step2_text", "step3_title", "step3_text",
        "video_title", "video_caption",
        "single_tile_text", "sets_tile_text",
        "custom_title", "custom_text", "custom_button_text",
        "newsletter_title", "newsletter_text",
        "footer_text",
        "price_note", "ships_in", "care_text", "shipping_text", "story_title", "story_text",
    )
