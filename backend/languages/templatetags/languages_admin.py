from django import template
from django.urls import reverse

from ..conf import NAMES, NATIVE_NAMES, SOURCE, TARGETS, provider_name
from ..report import collect_missing, totals

register = template.Library()

PROVIDER_LABELS = {"claude": "Claude", "google": "Google Translate"}


@register.simple_tag
def languages_config():
    """Settings for languages/admin.js (read from a JSON script tag)."""
    provider = provider_name()
    return {
        "source": SOURCE,
        "targets": list(TARGETS),
        "names": NAMES,
        "nativeNames": NATIVE_NAMES,
        "translateUrl": reverse("languages_translate"),
        "missingUrl": reverse("languages_missing"),
        "enabled": bool(provider),
        "provider": PROVIDER_LABELS.get(provider, ""),
    }


@register.inclusion_tag("admin/languages/panel.html")
def languages_panel():
    """The "Translations" box on the admin home page."""
    items = collect_missing()
    counts = totals(items)
    return {
        "items_count": len(items),
        "rows": [(NAMES[lang], counts[lang]) for lang in TARGETS],
        "missing_url": reverse("languages_missing"),
        "provider": PROVIDER_LABELS.get(provider_name(), ""),
    }
