from modeltranslation.translator import TranslationOptions


class ShopTranslationOptions(TranslationOptions):
    """Translation settings shared by every model.

    An empty translation always shows the English text. (By default the library only does
    that when the value equals the field's default, so fields with default texts would
    show up empty.)
    """

    fallback_undefined = ""
