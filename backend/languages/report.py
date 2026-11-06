"""Which texts still need an Armenian or Russian version, and where to fix them."""

from dataclasses import dataclass, field

from django.contrib import admin
from django.db import models
from django.urls import NoReverseMatch, reverse
from modeltranslation.translator import translator

from .conf import TARGETS, missing_translations


@dataclass
class MissingItem:
    section: str  # e.g. "Candles" or "Candle care page"
    label: str  # the object, e.g. "Holly Bauble Candle" or "Tip: Trim the wick"
    url: str  # its admin page (for inline rows: the page they are edited on)
    missing: dict[str, list[str]] = field(default_factory=dict)

    @property
    def counts(self):
        return {lang: len(fields) for lang, fields in self.missing.items()}

    @property
    def cells(self):
        """Missing field names per language, in TARGETS order (for table columns)."""
        return [[f.replace("_", " ") for f in self.missing[lang]] for lang in TARGETS]


def _admin_url(obj) -> str:
    opts = obj._meta
    try:
        return reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
    except NoReverseMatch:
        return ""


def _edited_on(obj):
    """The object whose admin page shows `obj`: itself, or the parent of an inline row."""
    if type(obj) in admin.site._registry:
        return obj
    for f in obj._meta.get_fields():
        if isinstance(f, models.ForeignKey) and f.related_model in admin.site._registry:
            parent = getattr(obj, f.name)
            if parent is not None:
                return parent
    return None


def _section(model) -> str:
    name = model._meta.verbose_name_plural
    return name[:1].upper() + name[1:]


def collect_missing() -> list[MissingItem]:
    items = []
    for model in translator.get_registered_models(abstract=False):
        for obj in model._default_manager.all():
            missing = missing_translations(obj)
            if not any(missing.values()):
                continue
            owner = _edited_on(obj)
            if owner is None:
                continue
            if owner is obj:
                section, label = _section(model), str(obj)
            else:
                section = _section(type(owner))
                label = f"{model._meta.verbose_name.capitalize()}: {obj}"
            items.append(MissingItem(section, label, _admin_url(owner), missing))
    items.sort(key=lambda item: (item.section, item.label))
    return items


def totals(items: list[MissingItem]) -> dict[str, int]:
    return {lang: sum(item.counts[lang] for item in items) for lang in TARGETS}
