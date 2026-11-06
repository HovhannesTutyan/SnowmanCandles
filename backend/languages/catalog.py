"""Ready-made Armenian and Russian versions of the shop's texts (content_translations.json).

They are used to fill empty translations: when the languages were added (the data
migration), by `seed_demo` and by `manage.py fill_translations`. Texts are matched by
their exact English wording, so an edited English text simply finds no entry.
"""

import json
from functools import lru_cache
from pathlib import Path

from .conf import SOURCE, TARGETS, localized

CATALOG_PATH = Path(__file__).with_name("content_translations.json")


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, dict[str, str]]:
    with CATALOG_PATH.open(encoding="utf-8") as f:
        return {_normalize(english): versions for english, versions in json.load(f).items()}


def translation_for(english: str, lang: str) -> str | None:
    entry = load_catalog().get(_normalize(english or ""))
    return entry.get(lang) if entry else None


def fill_from_catalog(obj, fields) -> bool:
    """Fill empty Armenian/Russian fields of `obj` from the catalog. Works on historical
    (migration) models too, as it only reads and writes the per-language attributes.
    Returns True if anything changed (the caller saves)."""
    changed = False
    for field in fields:
        english = getattr(obj, localized(field, SOURCE)) or ""
        if not english.strip():
            continue
        for lang in TARGETS:
            name = localized(field, lang)
            current = (getattr(obj, name) or "").strip()
            # A "translation" identical to the English text counts as missing.
            if current and current != english.strip():
                continue
            text = translation_for(english, lang)
            if text and text != current:
                setattr(obj, name, text)
                changed = True
    return changed


def fill_all_from_catalog() -> int:
    """Fill every empty translation in the database that the catalog knows. Returns the
    number of rows changed."""
    from modeltranslation.translator import translator

    from .conf import translated_fields

    changed_rows = 0
    for model in translator.get_registered_models(abstract=False):
        fields = translated_fields(model)
        columns = [localized(f, lang) for f in fields for lang in TARGETS]
        for obj in model._default_manager.all():
            if fill_from_catalog(obj, fields):
                obj.save(update_fields=columns)
                changed_rows += 1
    return changed_rows
