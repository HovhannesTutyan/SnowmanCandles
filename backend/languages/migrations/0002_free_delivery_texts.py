"""Delivery is now free and takes 1–2 days: update the site texts that said otherwise
(only where they still have the old default wording), and translate the new basket texts."""

from django.db import migrations

OLD_TO_NEW = {
    "price_note": (
        "Tax included. Shipping calculated at checkout.",
        "Tax included. Free delivery in 1–2 days.",
    ),
    "ships_in": ("3–5 days", "1–2 days"),
    "shipping_text": (
        "Every piece is wrapped by hand and sent with tracking. As each candle is made by hand, "
        "please get in touch within 14 days if anything arrives damaged and we'll make it right.",
        "Delivery is free and takes 1–2 days. Every piece is wrapped by hand, and as each candle "
        "is made by hand, please get in touch within 14 days if anything arrives damaged and "
        "we'll make it right.",
    ),
}
NEW_FIELDS = ["delivery_text", "order_success_text"]


def update(apps, schema_editor):
    from languages.catalog import translation_for

    content = apps.get_model("home", "HomePageContent").objects.filter(pk=1).first()
    if content is None:
        return  # created later with the new defaults (HomePageContent.load fills translations)
    for field, (old, new) in OLD_TO_NEW.items():
        if (getattr(content, f"{field}_en") or "").strip() == old:
            setattr(content, field, new)
            setattr(content, f"{field}_en", new)
            for lang in ("hy", "ru"):
                setattr(content, f"{field}_{lang}", translation_for(new, lang) or "")
    for field in NEW_FIELDS:
        english = getattr(content, f"{field}_en") or getattr(content, field)
        setattr(content, f"{field}_en", english)
        for lang in ("hy", "ru"):
            setattr(content, f"{field}_{lang}", translation_for(english, lang) or "")
    content.save()


class Migration(migrations.Migration):
    dependencies = [
        ("languages", "0001_fill_translations"),
        ("home", "0006_homepagecontent_delivery_text_and_more"),
    ]

    operations = [migrations.RunPython(update, migrations.RunPython.noop)]
