from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Chapter,
    ChapterCard,
    ChapterPoint,
    ChapterQuestion,
    ChapterSwatch,
    IngredientsPage,
)

COLOR_WIDGET = forms.TextInput(attrs={"type": "color"})


def photo_preview(image):
    if not image:
        return "No photo: the drawn illustration from the design is shown."
    return format_html(
        '<img src="{}" alt="" style="max-width:320px;max-height:180px;border-radius:6px;">',
        image.url,
    )


@admin.register(IngredientsPage)
class IngredientsPageAdmin(admin.ModelAdmin):
    """Hero and closing texts. A single page: the list view jumps straight to the form."""

    readonly_fields = ["hero_image_preview", "updated_at"]
    fieldsets = [
        ("Hero", {"fields": [
            "hero_eyebrow", "hero_title", "hero_text", "hero_link_text",
            ("hero_image", "hero_image_preview"), "hero_image_label",
        ]}),
        ("Closing call to action", {"fields": ["cta_title", "cta_text", "cta_button_text"]}),
        ("Chapter bar", {
            "fields": ["nav_title"],
            "description": "The chapters themselves are edited under Ingredients → Chapters.",
        }),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]

    @admin.display(description="Current")
    def hero_image_preview(self, obj):
        return photo_preview(obj.hero_image)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = IngredientsPage.load()
        return redirect(reverse("admin:ingredients_ingredientspage_change", args=[obj.pk]))


class ItemInline(admin.TabularInline):
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "color":
            kwargs["widget"] = COLOR_WIDGET
        elif db_field.name == "answer":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 3, "cols": 60})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class PointInline(ItemInline):
    model = ChapterPoint
    fields = ["lead", "text", "order"]
    verbose_name_plural = "Bullet points"


class QuestionInline(ItemInline):
    model = ChapterQuestion
    fields = ["question", "answer", "order"]
    verbose_name_plural = "Questions (expandable, next to the text)"


class CardInline(ItemInline):
    model = ChapterCard
    fields = ["icon", "title", "text", "order"]
    verbose_name_plural = "Cards (under the text, with the cards title above)"


class SwatchInline(ItemInline):
    model = ChapterSwatch
    fields = ["color", "name", "note", "order"]
    verbose_name_plural = "Colour swatches"


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "nav_label", "anchor", "order", "is_published"]
    list_display_links = ["title"]
    list_editable = ["order", "is_published"]
    list_filter = ["is_published"]
    search_fields = ["title", "intro", "body"]
    prepopulated_fields = {"anchor": ["nav_label"]}
    readonly_fields = ["banner_image_preview"]
    fieldsets = [
        (None, {"fields": [("title", "nav_label"), "anchor", ("order", "is_published")]}),
        ("Banner", {"fields": [
            "intro", "illustration", ("banner_image", "banner_image_preview"),
            ("banner_color", "banner_text"),
        ]}),
        ("Text", {"fields": ["body", "cards_title"]}),
    ]
    inlines = [PointInline, QuestionInline, CardInline, SwatchInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "banner_color":
            kwargs["widget"] = COLOR_WIDGET
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Current")
    def banner_image_preview(self, obj):
        return photo_preview(obj.banner_image)
