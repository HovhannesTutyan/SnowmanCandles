"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import (
    Chapter,
    ChapterCard,
    ChapterPoint,
    ChapterQuestion,
    ChapterSwatch,
    IngredientsPage,
)


@register(IngredientsPage)
class IngredientsPageTranslation(ShopTranslationOptions):
    fields = (
        "nav_title", "hero_eyebrow", "hero_title", "hero_text", "hero_link_text",
        "hero_image_label", "cta_title", "cta_text", "cta_button_text",
    )


@register(Chapter)
class ChapterTranslation(ShopTranslationOptions):
    fields = ("nav_label", "title", "intro", "body", "cards_title")


@register(ChapterPoint)
class ChapterPointTranslation(ShopTranslationOptions):
    fields = ("lead", "text")


@register(ChapterQuestion)
class ChapterQuestionTranslation(ShopTranslationOptions):
    fields = ("question", "answer")


@register(ChapterCard)
class ChapterCardTranslation(ShopTranslationOptions):
    fields = ("title", "text")


@register(ChapterSwatch)
class ChapterSwatchTranslation(ShopTranslationOptions):
    fields = ("name", "note")
