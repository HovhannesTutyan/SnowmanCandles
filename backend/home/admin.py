from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import CONTENT_IMAGE_FIELDS, LINK_HELP, HeroSlide, HomePageContent


def image_preview_html(image, max_height=160):
    if not image:
        return "Using the image from the original design."
    return format_html(
        '<img src="{}" alt="" style="max-width:320px;max-height:{}px;'
        'border-radius:6px;background:#ECEFEA;padding:8px;">',
        image.url,
        max_height,
    )


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    """Site-wide texts and images. A single page: the list view jumps straight to the form."""

    readonly_fields = [f"{name}_preview" for name in CONTENT_IMAGE_FIELDS] + ["updated_at"]
    fieldsets = [
        ("Brand", {"fields": ["studio_name", "accent_color", "currency", "ticker_messages"]}),
        ("Hero", {
            "fields": ["hero_eyebrow", "hero_title", "hero_text",
                       "hero_button_text", "hero_video_button_text"],
            "description": "The rotating pieces on the right are managed under "
                           "Home → Hero slides.",
        }),
        ("Winter collection grid", {
            "fields": ["collection_eyebrow", "collection_title"],
            "description": "The cards show featured candles and collections "
                           "(tick “Is featured” on an item).",
        }),
        ("How it's made", {"fields": [
            "made_title", "made_text",
            ("made_before_image", "made_before_image_preview"),
            ("made_after_image", "made_after_image_preview"),
            ("step1_title", "step1_text"),
            ("step2_title", "step2_text"),
            ("step3_title", "step3_text"),
            "video_title", "video_caption", "video_url",
            ("video_image", "video_image_preview"),
        ]}),
        ("Shop by type", {"fields": [
            "single_tile_text", ("single_tile_image", "single_tile_image_preview"),
            "sets_tile_text", ("sets_tile_image", "sets_tile_image_preview"),
        ]}),
        ("Custom orders", {"fields": [
            "custom_title", "custom_text", "custom_button_text",
            ("custom_image_1", "custom_image_1_preview"),
            ("custom_image_2", "custom_image_2_preview"),
        ]}),
        ("Newsletter", {"fields": ["newsletter_title", "newsletter_text"]}),
        ("Footer & contact", {"fields": [
            "footer_text", "contact_email", "contact_phone", "instagram_handle",
        ]}),
        ("Product pages", {
            "fields": ["price_note", "ships_in", "care_text", "shipping_text",
                       "story_title", "story_text"],
            "description": "Shared by every product page. A product's own making-of text "
                           "(on the product) replaces the making-of text here.",
        }),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "accent_color":
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = HomePageContent.load()
        return redirect(reverse("admin:home_homepagecontent_change", args=[obj.pk]))


def _make_preview(field_name):
    @admin.display(description="Current")
    def preview(self, obj):
        return image_preview_html(getattr(obj, field_name))

    return preview


# Adds the read-only `<image field>_preview` methods listed in readonly_fields.
for _name in CONTENT_IMAGE_FIELDS:
    setattr(HomePageContentAdmin, f"{_name}_preview", _make_preview(_name))


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["thumbnail", "title", "linked_item", "order", "is_active"]
    list_display_links = ["thumbnail", "title"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["title", "subtitle"]
    autocomplete_fields = ["candle", "collection"]
    readonly_fields = ["image_preview", "created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["title", "subtitle", "button_text"]}),
        ("Image", {"fields": ["image", "image_preview"]}),
        ("Link", {"fields": ["candle", "collection"], "description": LINK_HELP}),
        ("Display", {"fields": ["order", "is_active"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("candle", "collection")

    @admin.display(description="Image")
    def thumbnail(self, obj):
        image = obj.display_image
        if not image:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="width:96px;height:40px;'
            'object-fit:cover;border-radius:4px;">',
            image.url,
        )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        image = obj.display_image
        if not image:
            return "No image yet."
        note = "" if obj.image else " (from the linked item)"
        return format_html(
            '<img src="{}" alt="" style="max-width:600px;max-height:250px;'
            'border-radius:6px;"><div>{}</div>',
            image.url,
            note,
        )

    @admin.display(description="Linked item")
    def linked_item(self, obj):
        if obj.candle:
            return f"Candle: {obj.candle}"
        if obj.collection:
            return f"Collection: {obj.collection}"
        return "-"
