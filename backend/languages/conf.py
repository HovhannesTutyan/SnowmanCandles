"""The shop's languages, and helpers for reading translated fields."""

from django.conf import settings
from modeltranslation.translator import NotRegistered, translator

SOURCE = "en"  # texts are written in English in the admin
TARGETS = ("hy", "ru")  # ...and translated into these
CODES = (SOURCE, *TARGETS)
NAMES = {"en": "English", "hy": "Armenian", "ru": "Russian"}
NATIVE_NAMES = {"en": "English", "hy": "Հայերեն", "ru": "Русский"}


def localized(field: str, lang: str) -> str:
    return f"{field}_{lang}"


def translated_fields(model) -> list[str]:
    """Names of the model's translated fields (without the language suffix)."""
    try:
        options = translator.get_options_for_model(model)
    except NotRegistered:
        return []
    return list(options.all_fields)


def localized_field_names(model) -> list[str]:
    """Every per-language column, e.g. ["title_en", "title_hy", "title_ru"]."""
    return [localized(f, lang) for f in translated_fields(model) for lang in CODES]


def missing_translations(obj) -> dict[str, list[str]]:
    """{"hy": [fields], "ru": [fields]}: fields with English text but no translation."""
    missing = {lang: [] for lang in TARGETS}
    for field in translated_fields(type(obj)):
        if not (getattr(obj, localized(field, SOURCE)) or "").strip():
            continue
        for lang in TARGETS:
            if not (getattr(obj, localized(field, lang)) or "").strip():
                missing[lang].append(field)
    return missing


def provider_name() -> str:
    """The configured machine-translation service, or "" when the button is off."""
    name = settings.TRANSLATION_PROVIDER
    return name if name in {"claude", "google"} and settings.TRANSLATION_API_KEY else ""
