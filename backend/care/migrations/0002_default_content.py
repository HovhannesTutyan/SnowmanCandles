"""Starting content for the care page, from the "Candle care & tips" design.

Adapted to the shop: every product is a candle, and the design's [placeholders]
are replaced with wording that needs no shop-specific facts. Everything can be
edited in the admin (Care → Candle care page).
"""

from django.db import migrations

TIPS = [
    (
        "Let the first burn go wide",
        "Wax remembers. On the very first light, let it burn until the melted pool reaches "
        "the edge — roughly an hour for every 2.5 cm of width. Blow it out too soon and it "
        "sets a “memory ring” it will follow forever after.",
    ),
    (
        "Trim before every light",
        "A wick of about 5 mm gives a calm, golden flame. Trim it once the wax has cooled, "
        "every time, and lift out any snipped ends so nothing but the wick ever burns.",
    ),
    (
        "Find it a quiet spot",
        "Choose a level, heat-safe surface away from open windows, fans and vents — drafts "
        "make flames flicker and soot. Keep candles at least 10 cm apart, and well away from "
        "curtains, shelves above, pets and little hands.",
    ),
    (
        "Know when to stop",
        "Retire the flame when about 1 cm of wax is left. Burning lower lets the heat reach "
        "the base of the holder — and in hand-painted plaster, that last centimetre is what "
        "keeps it safe and lovely.",
    ),
]

RITUALS = [
    (
        "Store them cool and dark",
        "Between burns, keep candles somewhere cool, dry and out of the way — a cupboard is "
        "perfect.",
    ),
    (
        "Dust with a soft, dry brush",
        "A clean make-up brush lifts dust from the painted details and the cool wax surface "
        "without scratching.",
    ),
    (
        "Keep water away from the holder",
        "Plaster is porous, so skip the sink. Wipe soot or marks with a dry, soft cloth — only "
        "once everything is completely cool.",
    ),
    (
        "Give the holder a second life",
        "When the candle is finished, the painted piece stays. Turn it into a home for rings, "
        "keys or sweets.",
    ),
    (
        "Keep out of direct sun",
        "Strong sunlight can fade hand-painted colours, soften wax and dull its tint. A shady "
        "shelf keeps both looking new.",
    ),
    (
        "Lids on, scent in",
        "For candles with a lid, like our baubles and the carousel, close the lid once the "
        "flame is out and the wax has cooled. It keeps dust off and the fragrance fresh for "
        "longer.",
    ),
]

FRAGRANCE_TIPS = [
    (
        "Give it time to bloom.",
        "Scent fills a room best once the melt pool is wide — usually 1 to 2 hours in. Small "
        "room, short burns; open-plan spaces, longer ones (never past 4 hours).",
    ),
    (
        "Put it out gently.",
        "Use a snuffer, or dip the wick into the melted wax and straighten it. You'll avoid "
        "the smoky smell that drowns the fragrance.",
    ),
    (
        "Keep the holder.",
        "Once cool, ease out the last wax with a wooden spoon and wipe the inside dry. The "
        "painted piece is yours to keep.",
    ),
]

FAQS = [
    (
        "How long should I burn my candle?",
        "Long enough for the melted pool to reach the edges — about an hour for every 2.5 cm "
        "of width, especially on the first burn. But never more than 4 hours at a time: after "
        "that the wick can “mushroom”, the flame grows and the holder gets too warm. Let it "
        "cool for at least two hours before relighting.",
    ),
    (
        "Why is my candle tunnelling?",
        "Tunnelling happens when early burns are too short, so the wax only melts down the "
        "middle. To rescue it, wrap a band of kitchen foil around the top so it overhangs the "
        "edge, leaving an opening in the centre, and let it burn for a couple of hours under "
        "supervision. The trapped heat melts the walls back to level.",
    ),
    (
        "Why is my candle smoking?",
        "Usually the wick is too long or there's a draft. Put the flame out, let it cool, trim "
        "the wick to about 5 mm and move the candle away from windows, fans or vents. Snuffing "
        "rather than blowing it out also stops that puff of smoke at the end.",
    ),
    (
        "Is soy wax better than other waxes?",
        "Each wax behaves differently. Soy is plant-based and burns softly and slowly; beeswax "
        "is naturally golden and burns long and bright; paraffin carries strong fragrance "
        "well. You'll find the wax used in each piece under “Details” on its product page.",
    ),
    (
        "Can I wash my painted holder?",
        "Please don't — plaster is porous and water can mark or soften it and lift the paint. "
        "Once the candle is out and completely cool, use a soft dry cloth or brush. Soot on "
        "the wax usually means the wick needs trimming.",
    ),
    (
        "How do I reuse the holder when the candle is finished?",
        "Stop when about 1 cm of wax remains. Once fully cool, ease the leftover wax out with "
        "a wooden spoon and wipe the inside with a dry paper towel. Your piece is ready to "
        "hold jewellery, keys, sweets or a tiny potted plant (keep the pot inside — no water "
        "on the plaster).",
    ),
]


def create_content(apps, schema_editor):
    CarePage = apps.get_model("care", "CarePage")
    page, created = CarePage.objects.get_or_create(pk=1)
    if not created and (page.tips.exists() or page.faqs.exists()):
        return  # content already there

    lists = [
        ("CareTip", TIPS, ("title", "text")),
        ("CareRitual", RITUALS, ("title", "text")),
        ("FragranceTip", FRAGRANCE_TIPS, ("lead", "text")),
        ("FAQ", FAQS, ("question", "answer")),
    ]
    for model_name, rows, (first, second) in lists:
        Model = apps.get_model("care", model_name)
        Model.objects.bulk_create(
            Model(page=page, order=order, **{first: a, second: b})
            for order, (a, b) in enumerate(rows, start=1)
        )


def remove_content(apps, schema_editor):
    apps.get_model("care", "CarePage").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("care", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_content, remove_content),
    ]
