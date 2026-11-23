from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import translation
from django.utils.html import format_html

from home.models import HomePageContent
from languages.admin import TranslatedAdmin
from languages.conf import CODES

from .models import SeoSettings
from .pages import auto_page_description, auto_page_title, auto_product_title, clip

PAGES = [
    ("home", "Home page"),
    ("care", "Candle care page"),
    ("ingredients", "Ingredients page"),
    ("decorate", "Decorate page"),
]

SEO_FIELDSET_DESCRIPTION = (
    "How this appears in Google and in shared links. The grey text in an empty box is "
    "what's used automatically, so you only need to fill in the boxes you want to change."
)


class AutomaticTextMixin:
    """Shows the automatic text as grey placeholder text in each empty SEO box."""

    def automatic_texts(self, obj, lang: str) -> dict[str, str]:
        """{field name: automatic text} for one language."""
        return {}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for lang in CODES:
            with translation.override(lang):
                texts = self.automatic_texts(obj, lang)
            for name, value in texts.items():
                field = form.base_fields.get(f"{name}_{lang}")
                if field is not None and value:
                    field.widget.attrs["placeholder"] = value
        return form


class ProductSeoMixin(AutomaticTextMixin):
    """For the candle and collection admins."""

    seo_fieldset = (
        "Search engines (SEO)",
        {
            "fields": ["seo_title", "seo_description"],
            "classes": ["collapse"],
            "description": SEO_FIELDSET_DESCRIPTION,
        },
    )

    def automatic_texts(self, obj, lang):
        if obj is None:
            return {}
        studio = HomePageContent.load().studio_name
        return {"seo_title": auto_product_title(obj, studio), "seo_description": clip(obj.description)}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name.startswith("seo_description"):
            kwargs["widget"] = forms.Textarea(attrs={"rows": 2, "cols": 80})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(SeoSettings)
class SeoSettingsAdmin(AutomaticTextMixin, TranslatedAdmin):
    """A single settings page: the list view jumps straight to the form."""

    readonly_fields = ["share_image_preview", "updated_at"]
    fieldsets = [
        *[
            (label, {"fields": [f"{key}_title", f"{key}_description"],
                     "description": SEO_FIELDSET_DESCRIPTION if key == "home" else ""})
            for key, label in PAGES
        ],
        ("Shared links", {"fields": ["share_image", "share_image_preview"]}),
        ("Delivery (for Google Shopping)", {
            "fields": ["delivery_country", ("delivery_days_min", "delivery_days_max")],
            "description": "Shown to Google with each product: free delivery, and how long it "
            "takes. Prices and stock come from the products themselves.",
        }),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]

    def automatic_texts(self, obj, lang):
        content = HomePageContent.load()
        texts = {}
        for key, _label in PAGES:
            texts[f"{key}_title"] = auto_page_title(lang, key, content.studio_name)
            texts[f"{key}_description"] = auto_page_description(lang, key, content)
        return texts

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if "_description" in db_field.name:
            kwargs["widget"] = forms.Textarea(attrs={"rows": 2, "cols": 80})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Current")
    def share_image_preview(self, obj):
        if not obj.share_image:
            return "No image: shared links use the first featured product's photo."
        return format_html(
            '<img src="{}" alt="" style="max-width:320px;max-height:180px;border-radius:6px;">',
            obj.share_image.url,
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SeoSettings.load()
        return redirect(reverse("admin:seo_seosettings_change", args=[obj.pk]))
