from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from languages.admin import TranslatedAdmin, TranslatedStackedInline

from .models import DecoratePage, GalleryImage, Room


def preview(image, size=160, empty="Using the picture from the original design."):
    if not image:
        return empty
    return format_html(
        '<img src="{}" alt="" style="max-width:{}px;max-height:{}px;border-radius:6px;">',
        image.url,
        size,
        size,
    )


class RoomInline(TranslatedStackedInline):
    model = Room
    fields = ["title", "text", ("picture", "picture_preview"), "order"]
    readonly_fields = ["picture_preview"]
    extra = 0
    verbose_name_plural = "Room cards (under the story)"

    @admin.display(description="Picture")
    def picture_preview(self, obj):
        return preview(obj.picture.image if obj.picture else None, 60, "-")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "picture":
            kwargs["queryset"] = GalleryImage.objects.order_by("order", "id")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(DecoratePage)
class DecoratePageAdmin(TranslatedAdmin):
    """A single page: the list view jumps straight to the form; rooms are edited inline."""

    readonly_fields = ["hero_video_preview", "hero_image_preview", "cta_image_preview", "updated_at"]
    fieldsets = [
        ("Hero", {"fields": [
            "hero_eyebrow", "hero_title", "hero_text", "hero_link_text",
            ("hero_video", "hero_video_preview"),
            ("hero_image", "hero_image_preview"), "hero_image_alt",
        ]}),
        ("Story", {"fields": ["story_title", "story_subtitle", "story_text"]}),
        ("Gallery heading", {
            "fields": ["gallery_title", "gallery_text"],
            "description": "The pictures themselves are under Decorate → Gallery images.",
        }),
        ("Closing call to action", {"fields": [
            "cta_title", "cta_text", "cta_button_text", ("cta_image", "cta_image_preview"),
        ]}),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]
    inlines = [RoomInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "hero_title":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 2, "cols": 40})
        elif db_field.name == "story_text":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 10, "cols": 90})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Current")
    def hero_video_preview(self, obj):
        if not obj.hero_video:
            return "No video: the hero picture is shown."
        return format_html(
            '<video src="{}" muted loop autoplay playsinline '
            'style="max-width:200px;max-height:260px;border-radius:6px;"></video>',
            obj.hero_video.url,
        )

    @admin.display(description="Current")
    def hero_image_preview(self, obj):
        return preview(obj.hero_image)

    @admin.display(description="Current")
    def cta_image_preview(self, obj):
        return preview(obj.cta_image)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = DecoratePage.load()
        return redirect(reverse("admin:decorate_decoratepage_change", args=[obj.pk]))


@admin.register(GalleryImage)
class GalleryImageAdmin(TranslatedAdmin):
    list_display = ["thumbnail", "caption", "order", "is_published", "translation_status"]
    list_display_links = ["thumbnail", "caption"]
    list_editable = ["order", "is_published"]
    list_filter = ["is_published"]
    search_fields = ["caption", "alt"]
    autocomplete_fields = ["products"]
    readonly_fields = ["image_preview"]
    fields = ["image", "image_preview", "caption", "alt", "products", ("order", "is_published")]

    @admin.display(description="Picture")
    def thumbnail(self, obj):
        return preview(obj.image, 60, "-")

    @admin.display(description="Preview")
    def image_preview(self, obj):
        return preview(obj.image, 320, "No picture uploaded yet.")
