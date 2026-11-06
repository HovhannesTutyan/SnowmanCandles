"""Base classes for admin pages with translated fields.

Each translated field shows as an English box with the Armenian and Russian boxes under
it (grouped and labelled by static/languages/admin.js). English is required; an empty
translation falls back to the English text on the site.
"""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import (
    TranslationAdmin,
    TranslationStackedInline,
    TranslationTabularInline,
)

from .conf import NAMES, TARGETS, missing_translations


class TranslatedAdmin(TranslationAdmin):
    """A ModelAdmin with translated fields. Add "translation_status" to list_display
    for a column showing which items still need translating."""

    @admin.display(description="Translations")
    def translation_status(self, obj):
        missing = missing_translations(obj)
        gaps = [NAMES[lang] for lang in TARGETS if missing[lang]]
        if not gaps:
            return format_html('<span class="lang-status is-done">✓ Translated</span>')
        return format_html(
            '<span class="lang-status is-missing" title="{}">Missing: {}</span>',
            "; ".join(f"{NAMES[lang]}: {', '.join(missing[lang])}" for lang in TARGETS if missing[lang]),
            ", ".join(gaps),
        )


class TranslatedStackedInline(TranslationStackedInline):
    pass


class TranslatedTabularInline(TranslationTabularInline):
    pass
