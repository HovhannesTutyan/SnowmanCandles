"""Starting texts for the decorate page and its room cards, from the design.

Gallery pictures are demo content: `python manage.py seed_demo` uploads the design's 16
pictures and links each room card to its picture.
"""

from django.db import migrations

ROOMS = [
    ("Living room", "A low tray of pillars makes the coffee table glow."),
    ("Bedroom", "One candle, one plaster piece — keep it calm."),
    ("Bathroom", "A plaster bauble for cotton pads by day, a flame by night."),
    ("Dining table", "Mix heights; choose unscented for dinner."),
    ("Entryway", "A plaster dish for keys, a candle to welcome."),
    ("Terrace & garden", "Gather candles on a tray, out of the breeze."),
]


def create_content(apps, schema_editor):
    DecoratePage = apps.get_model("decorate", "DecoratePage")
    Room = apps.get_model("decorate", "Room")
    page, _ = DecoratePage.objects.get_or_create(pk=1)
    if not Room.objects.filter(page=page).exists():
        Room.objects.bulk_create(
            Room(page=page, title=title, text=text, order=order)
            for order, (title, text) in enumerate(ROOMS, start=1)
        )


def remove_content(apps, schema_editor):
    apps.get_model("decorate", "DecoratePage").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("decorate", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_content, remove_content),
    ]
