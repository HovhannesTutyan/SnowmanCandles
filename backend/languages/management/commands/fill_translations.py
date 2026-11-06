from django.core.management.base import BaseCommand

from languages.catalog import fill_all_from_catalog
from languages.report import collect_missing, totals


class Command(BaseCommand):
    help = (
        "Fills empty Armenian and Russian texts from the built-in translations "
        "(languages/content_translations.json). Never overwrites a translation."
    )

    def handle(self, *args, **options):
        changed = fill_all_from_catalog()
        self.stdout.write(self.style.SUCCESS(f"Filled translations on {changed} item(s)."))
        left = totals(collect_missing())
        if any(left.values()):
            self.stdout.write(
                f"Still missing: {left['hy']} Armenian, {left['ru']} Russian text(s). "
                "See Admin → Translations."
            )
        else:
            self.stdout.write("Every text has an Armenian and a Russian version.")
