from django.db import migrations, models

# Keepsake jars and figurines were dropped: every product is a candle, sold either
# on its own or as a multi-piece set.
OLD_TYPES = ["keepsake_jar", "figurine"]


def old_types_to_candle(apps, schema_editor):
    Candle = apps.get_model("shop", "Candle")
    Candle.objects.filter(product_type__in=OLD_TYPES).update(product_type="candle")


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_candle_product_type_candle_tint_collection_tint_and_more"),
    ]

    operations = [
        migrations.RunPython(old_types_to_candle, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="candle",
            name="product_type",
            field=models.CharField(
                choices=[("candle", "Single candle"), ("set", "Candle set")],
                db_index=True,
                default="candle",
                help_text="Single candle: one piece (e.g. the roadster). Candle set: more than "
                "one piece, e.g. a wood candle with plaster snowmen around it.",
                max_length=20,
                verbose_name="type",
            ),
        ),
    ]
