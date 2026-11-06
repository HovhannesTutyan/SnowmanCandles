"""Fields with an Armenian and Russian version next to the English one (see languages/)."""

from modeltranslation.translator import register

from languages.options import ShopTranslationOptions

from .models import FAQ, CarePage, CareRitual, CareTip, FragranceTip


@register(CarePage)
class CarePageTranslation(ShopTranslationOptions):
    fields = (
        "hero_title", "hero_text", "tips_eyebrow", "rituals_title",
        "fragrance_eyebrow", "fragrance_title", "fragrance_text", "faq_title",
    )


@register(CareTip)
@register(CareRitual)
class TitledItemTranslation(ShopTranslationOptions):
    fields = ("title", "text")


@register(FragranceTip)
class FragranceTipTranslation(ShopTranslationOptions):
    fields = ("lead", "text")


@register(FAQ)
class FAQTranslation(ShopTranslationOptions):
    fields = ("question", "answer")
