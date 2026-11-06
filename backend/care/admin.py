from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from languages.admin import TranslatedAdmin, TranslatedStackedInline

from .models import FAQ, CarePage, CareRitual, CareTip, FragranceTip


class ItemInline(TranslatedStackedInline):
    extra = 0
    classes = ["collapse"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {"text", "answer"}:
            kwargs["widget"] = forms.Textarea(attrs={"rows": 3, "cols": 80})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class CareTipInline(ItemInline):
    model = CareTip
    fields = ["title", "text", "order"]
    verbose_name = "tip"
    verbose_name_plural = "Tips (numbered 01, 02, … in this order)"


class CareRitualInline(ItemInline):
    model = CareRitual
    fields = ["title", "text", "order"]
    verbose_name = "care ritual"
    verbose_name_plural = "Care rituals"


class FragranceTipInline(ItemInline):
    model = FragranceTip
    fields = ["lead", "text", "order"]
    verbose_name = "fragrance point"
    verbose_name_plural = "Fragrance points"


class FAQInline(ItemInline):
    model = FAQ
    fields = ["question", "answer", "order"]
    verbose_name = "question"
    verbose_name_plural = "FAQs"


def photo_preview(image):
    if not image:
        return "No photo: the page shows the candlelit scene from the design."
    return format_html(
        '<img src="{}" alt="" style="max-width:320px;max-height:180px;border-radius:6px;">',
        image.url,
    )


@admin.register(CarePage)
class CarePageAdmin(TranslatedAdmin):
    """A single page: the list view jumps straight to the form; lists are edited inline."""

    autocomplete_fields = ["fragrance_product"]
    readonly_fields = ["hero_image_preview", "fragrance_image_preview", "updated_at"]
    fieldsets = [
        ("Hero", {"fields": ["hero_title", "hero_text", ("hero_image", "hero_image_preview")]}),
        ("Section headings", {"fields": ["tips_eyebrow", "rituals_title", "faq_title"]}),
        ("Fragrance section", {"fields": [
            "fragrance_eyebrow", "fragrance_title", "fragrance_text",
            ("fragrance_image", "fragrance_image_preview"), "fragrance_product",
        ]}),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]
    inlines = [CareTipInline, CareRitualInline, FragranceTipInline, FAQInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "hero_title":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 2, "cols": 40})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Current")
    def hero_image_preview(self, obj):
        return photo_preview(obj.hero_image)

    @admin.display(description="Current")
    def fragrance_image_preview(self, obj):
        return photo_preview(obj.fragrance_image)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = CarePage.load()
        return redirect(reverse("admin:care_carepage_change", args=[obj.pk]))
