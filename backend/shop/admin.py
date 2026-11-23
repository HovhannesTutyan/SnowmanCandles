from django import forms
from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html

from languages.admin import TranslatedAdmin, TranslatedStackedInline
from seo.admin import ProductSeoMixin

from .models import (
    LOW_STOCK_THRESHOLD,
    Candle,
    CandleImage,
    CandleShowcaseView,
    Collection,
    CollectionImage,
    CollectionShowcaseView,
    Scent,
)

PRODUCT_PAGE_FIELDSET = (
    "Product page",
    {"fields": ["scents", ("burn_time", "size"), "details", "story_title", "story_text"]},
)
LIT_VIEW_FIELDSET = (
    "Lit view (optional)",
    {
        "fields": [("flame_x", "flame_y"), "flame_preview"],
        "description": "Mark where the wick is on the main image to add a “Lit” view with an "
        "animated flame to the product page. Save to update the preview.",
    },
)


class GalleryInline(TranslatedStackedInline):
    fields = [("image", "preview"), "label", "order"]
    readonly_fields = ["preview"]
    extra = 0
    verbose_name = "extra photo"
    verbose_name_plural = "Extra photos (product page gallery)"

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.image:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="height:60px;border-radius:4px;">', obj.image.url
        )


class ShowcaseViewInline(TranslatedStackedInline):
    fields = [
        ("image", "preview"),
        "label",
        "short_label",
        "caption",
        ("color", "tint"),
        ("group", "order"),
    ]
    readonly_fields = ["preview"]
    extra = 0
    verbose_name = "showcase view"
    verbose_name_plural = (
        "Showcase views: the animated viewer at the top of the product page. Add transparent "
        "cut-outs in the same size, product at the bottom. No views: the regular gallery only."
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {"color", "tint"}:
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.image:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="height:90px;border-radius:6px;background:{};padding:4px;">',
            obj.image.url,
            obj.tint,
        )


class CandleShowcaseViewInline(ShowcaseViewInline):
    model = CandleShowcaseView


class CollectionShowcaseViewInline(ShowcaseViewInline):
    model = CollectionShowcaseView


class CandleImageInline(GalleryInline):
    model = CandleImage


class CollectionImageInline(GalleryInline):
    model = CollectionImage


@admin.register(Scent)
class ScentAdmin(TranslatedAdmin):
    list_display = ["name", "translation_status", "order"]
    list_editable = ["order"]
    search_fields = ["name"]


class AvailabilityFilter(admin.SimpleListFilter):
    title = "availability"
    parameter_name = "availability"

    def lookups(self, request, model_admin):
        return [
            ("in_stock", "In stock"),
            ("low_stock", "Low stock"),
            ("out_of_stock", "Out of stock"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "in_stock":
            return queryset.filter(stock__gt=LOW_STOCK_THRESHOLD)
        if value == "low_stock":
            return queryset.filter(stock__gte=1, stock__lte=LOW_STOCK_THRESHOLD)
        if value == "out_of_stock":
            return queryset.filter(stock=0)
        return queryset


class BaseItemAdmin(ProductSeoMixin, TranslatedAdmin):
    list_display = [
        "thumbnail", "title", "price", "stock", "availability", "translation_status",
        "is_featured", "featured_order",
    ]
    list_display_links = ["thumbnail", "title"]
    list_editable = ["price", "stock", "is_featured", "featured_order"]
    list_filter = [AvailabilityFilter, "is_featured", "created_at"]
    # Also required by the HeroSlide admin's autocomplete_fields.
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["image_preview", "flame_preview", "created_at", "updated_at"]
    actions = ["mark_out_of_stock", "add_to_featured", "remove_from_featured"]
    list_per_page = 25

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "tint":
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if not obj.image:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="width:50px;height:50px;'
            'object-fit:cover;border-radius:4px;">',
            obj.image.url,
        )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj.image:
            return "No image uploaded yet."
        return format_html(
            '<img src="{}" alt="" style="max-width:400px;max-height:400px;'
            'border-radius:6px;background:{};padding:12px;">',
            obj.image.url,
            obj.tint,
        )

    @admin.display(description="Flame position")
    def flame_preview(self, obj):
        if not obj.image:
            return "Upload a main image first."
        if not obj.flame:
            return "No wick position set: the product page has no “Lit” view."
        # A dot over the main image, placed the same way the site places the flame.
        return format_html(
            '<div style="position:relative;display:inline-block;background:#183A2C;'
            'padding:12px;border-radius:6px;">'
            '<div style="position:relative;display:inline-block;">'
            '<img src="{}" alt="" style="display:block;max-width:320px;max-height:240px;">'
            '<span style="position:absolute;left:{}%;bottom:{}%;width:14px;height:14px;'
            'margin-left:-7px;margin-bottom:-7px;border-radius:50%;background:#FFB23E;'
            'box-shadow:0 0 0 3px #fff,0 0 14px 4px rgba(255,178,62,.8);"></span>'
            "</div></div>",
            obj.image.url,
            obj.flame["x"],
            obj.flame["y"],
        )

    @admin.display(description="Availability", ordering="stock")
    def availability(self, obj):
        if not obj.is_available:
            label, color = "Out of stock", "#c62828"
        elif obj.is_low_stock:
            label, color = "Low stock", "#ef6c00"
        else:
            label, color = "In stock", "#2e7d32"
        return format_html(
            '<span style="color:{};font-weight:600;">&#9679; {}</span>', color, label
        )

    @admin.action(description="Mark as out of stock")
    def mark_out_of_stock(self, request, queryset):
        # .update() skips save(), so bump updated_at manually.
        updated = queryset.update(stock=0, updated_at=timezone.now())
        self.message_user(request, f"{updated} item(s) marked as out of stock.")

    @admin.action(description="Add to homepage featured")
    def add_to_featured(self, request, queryset):
        updated = queryset.update(is_featured=True, updated_at=timezone.now())
        self.message_user(request, f"{updated} item(s) added to homepage featured.")

    @admin.action(description="Remove from homepage featured")
    def remove_from_featured(self, request, queryset):
        updated = queryset.update(is_featured=False, updated_at=timezone.now())
        self.message_user(request, f"{updated} item(s) removed from homepage featured.")


@admin.register(Candle)
class CandleAdmin(BaseItemAdmin):
    list_display = [
        "thumbnail", "title", "product_type", "price", "stock", "availability",
        "translation_status", "is_featured", "featured_order",
    ]
    list_filter = [AvailabilityFilter, "product_type", "is_featured", "created_at"]
    fieldsets = [
        (None, {"fields": ["title", "slug", "product_type", "description"]}),
        ("Image", {"fields": ["image", "image_preview", "tint"]}),
        ("Pricing & stock", {"fields": ["price", "stock"]}),
        ("Homepage", {"fields": ["is_featured", "featured_order"]}),
        PRODUCT_PAGE_FIELDSET,
        LIT_VIEW_FIELDSET,
        ProductSeoMixin.seo_fieldset,
        ("Timestamps", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
    filter_horizontal = ["scents"]
    inlines = [CandleShowcaseViewInline, CandleImageInline]


@admin.register(Collection)
class CollectionAdmin(BaseItemAdmin):
    list_display = [
        "thumbnail", "title", "price", "stock", "availability", "candle_count",
        "translation_status", "is_featured", "featured_order",
    ]
    filter_horizontal = ["candles", "scents"]
    inlines = [CollectionShowcaseViewInline, CollectionImageInline]
    fieldsets = [
        (None, {"fields": ["title", "slug", "description"]}),
        ("Image", {"fields": ["image", "image_preview", "tint"]}),
        ("Pricing & stock", {"fields": ["price", "stock"]}),
        ("Homepage", {"fields": ["is_featured", "featured_order"]}),
        ("Candles in this collection", {"fields": ["candles"]}),
        PRODUCT_PAGE_FIELDSET,
        LIT_VIEW_FIELDSET,
        ProductSeoMixin.seo_fieldset,
        ("Timestamps", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        # Explicit order_by: GROUP BY from the annotation drops Meta.ordering, which
        # the HeroSlide autocomplete (paginated) needs.
        return (
            super()
            .get_queryset(request)
            .annotate(_candle_count=Count("candles"))
            .order_by(*Collection._meta.ordering)
        )

    @admin.display(description="Candles", ordering="_candle_count")
    def candle_count(self, obj):
        return obj._candle_count
