"""Fills the new per-language columns of existing rows.

Adding a column per language copied each field's *default* into every language, not the
row's actual text. This copies the real (English) text into the English column, then fills
Armenian and Russian from content_translations.json; translations it has no entry for are
left empty (the site then shows English) instead of repeating the English default.
"""

from django.db import migrations

# app label -> model -> translated fields (as registered in each app's translation.py
# when the languages were added).
FIELDS = {
    "shop": {
        "Scent": ["name"],
        "Candle": ["title", "description", "burn_time", "size", "details", "story_title", "story_text"],
        "Collection": ["title", "description", "burn_time", "size", "details", "story_title", "story_text"],
        "CandleImage": ["label"],
        "CollectionImage": ["label"],
        "CandleShowcaseView": ["label", "short_label", "caption"],
        "CollectionShowcaseView": ["label", "short_label", "caption"],
    },
    "home": {
        "HeroSlide": ["title", "subtitle", "button_text"],
        "HomePageContent": [
            "ticker_messages", "hero_eyebrow", "hero_title", "hero_text", "hero_button_text",
            "hero_video_button_text", "collection_eyebrow", "collection_title", "made_title",
            "made_text", "step1_title", "step1_text", "step2_title", "step2_text", "step3_title",
            "step3_text", "video_title", "video_caption", "single_tile_text", "sets_tile_text",
            "custom_title", "custom_text", "custom_button_text", "newsletter_title",
            "newsletter_text", "footer_text", "price_note", "ships_in", "care_text",
            "shipping_text", "story_title", "story_text",
        ],
    },
    "care": {
        "CarePage": [
            "hero_title", "hero_text", "tips_eyebrow", "rituals_title", "fragrance_eyebrow",
            "fragrance_title", "fragrance_text", "faq_title",
        ],
        "CareTip": ["title", "text"],
        "CareRitual": ["title", "text"],
        "FragranceTip": ["lead", "text"],
        "FAQ": ["question", "answer"],
    },
    "ingredients": {
        "IngredientsPage": [
            "nav_title", "hero_eyebrow", "hero_title", "hero_text", "hero_link_text",
            "hero_image_label", "cta_title", "cta_text", "cta_button_text",
        ],
        "Chapter": ["nav_label", "title", "intro", "body", "cards_title"],
        "ChapterPoint": ["lead", "text"],
        "ChapterQuestion": ["question", "answer"],
        "ChapterCard": ["title", "text"],
        "ChapterSwatch": ["name", "note"],
    },
    "decorate": {
        "DecoratePage": [
            "hero_eyebrow", "hero_title", "hero_text", "hero_link_text", "hero_image_alt",
            "story_title", "story_subtitle", "story_text", "gallery_title", "gallery_text",
            "cta_title", "cta_text", "cta_button_text",
        ],
        "GalleryImage": ["caption", "alt"],
        "Room": ["title", "text"],
    },
}


def fill(apps, schema_editor):
    from languages.catalog import translation_for

    for app_label, models in FIELDS.items():
        for model_name, fields in models.items():
            model = apps.get_model(app_label, model_name)
            for obj in model.objects.all():
                for field in fields:
                    english = getattr(obj, field) or ""
                    setattr(obj, f"{field}_en", english)
                    for lang in ("hy", "ru"):
                        setattr(obj, f"{field}_{lang}", translation_for(english, lang) or "")
                obj.save(update_fields=[f"{f}_{lang}" for f in fields for lang in ("en", "hy", "ru")])


class Migration(migrations.Migration):
    dependencies = [
        ("care", "0003_carepage_faq_title_en_carepage_faq_title_hy_and_more"),
        ("decorate", "0003_decoratepage_cta_button_text_en_and_more"),
        ("home", "0005_heroslide_button_text_en_heroslide_button_text_hy_and_more"),
        ("ingredients", "0003_chapter_body_en_chapter_body_hy_chapter_body_ru_and_more"),
        ("shop", "0008_candle_burn_time_en_candle_burn_time_hy_and_more"),
    ]

    operations = [migrations.RunPython(fill, migrations.RunPython.noop)]
