from django.db import migrations, models

SECTION_IMAGE_HELP = "Optional. If empty, the image from the original design is used."

# Texts that mentioned keepsakes, jars or figurines: (field, old default, new default).
# Only rows still showing the old default are updated, so edits made in the admin are kept.
TEXT_CHANGES = [
    (
        "hero_title",
        "Little keepsakes for the longest nights.",
        "Little candles for the longest nights.",
    ),
    (
        "hero_text",
        "Candles, lidded jars and winter figurines — each one cast in plaster and painted "
        "by hand, so no two are ever quite the same.",
        "Single candles and candle sets — each one cast in plaster, painted by hand and "
        "poured with wax, so no two are ever quite the same.",
    ),
    (
        "made_text",
        "Watch a plain plaster bauble become a painted keepsake — the same slow process "
        "behind every piece in the shop.",
        "Watch a plain plaster bauble become a painted candle — the same slow process "
        "behind every piece in the shop.",
    ),
    (
        "single_tile_text",
        "Painted holders, poured and ready to light",
        "One hand-painted piece, poured and ready to light",
    ),
    (
        "sets_tile_text",
        "Lidded baubles for rings, sweets and tiny treasures",
        "Little winter scenes with a candle at their heart",
    ),
    (
        "footer_text",
        "Hand-cast, hand-painted candles and keepsakes.",
        "Hand-cast, hand-painted candles and candle sets.",
    ),
]


def update_texts(apps, schema_editor, forward=True):
    HomePageContent = apps.get_model("home", "HomePageContent")
    for field, old, new in TEXT_CHANGES:
        before, after = (old, new) if forward else (new, old)
        HomePageContent.objects.filter(**{field: before}).update(**{field: after})


def revert_texts(apps, schema_editor):
    update_texts(apps, schema_editor, forward=False)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_homepagecontent"),
    ]

    operations = [
        # Candles tile -> single candles; jars tile -> candle sets; figurines tile removed.
        migrations.RenameField("homepagecontent", "candles_tile_text", "single_tile_text"),
        migrations.RenameField("homepagecontent", "candles_tile_image", "single_tile_image"),
        migrations.RenameField("homepagecontent", "jars_tile_text", "sets_tile_text"),
        migrations.RenameField("homepagecontent", "jars_tile_image", "sets_tile_image"),
        migrations.RemoveField("homepagecontent", "figurines_tile_text"),
        migrations.RemoveField("homepagecontent", "figurines_tile_image"),
        migrations.AlterField(
            model_name="homepagecontent",
            name="hero_title",
            field=models.CharField(default="Little candles for the longest nights.", max_length=160),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="hero_text",
            field=models.TextField(default=TEXT_CHANGES[1][2]),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="made_text",
            field=models.TextField(default=TEXT_CHANGES[2][2]),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="single_tile_text",
            field=models.CharField(
                default="One hand-painted piece, poured and ready to light",
                max_length=120,
                verbose_name="single candles tile text",
            ),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="sets_tile_text",
            field=models.CharField(
                default="Little winter scenes with a candle at their heart",
                max_length=120,
                verbose_name="candle sets tile text",
            ),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="single_tile_image",
            field=models.ImageField(blank=True, help_text=SECTION_IMAGE_HELP, upload_to="homepage/"),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="sets_tile_image",
            field=models.ImageField(blank=True, help_text=SECTION_IMAGE_HELP, upload_to="homepage/"),
        ),
        migrations.AlterField(
            model_name="homepagecontent",
            name="footer_text",
            field=models.CharField(
                default="Hand-cast, hand-painted candles and candle sets.", max_length=255
            ),
        ),
        migrations.RunPython(update_texts, revert_texts),
    ]
