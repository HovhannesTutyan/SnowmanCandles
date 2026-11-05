"""Starting content for the ingredients page, from the "What's inside our candles" design.

The design's [placeholders] are replaced with wording that makes no claims the shop
hasn't confirmed (fragrance standards, percentages); everything is editable in the
admin (Ingredients → Chapters).
"""

from django.db import migrations

CHAPTERS = [
    {
        "anchor": "soy",
        "nav_label": "Soy Wax",
        "title": "Soy wax",
        "intro": "The fuel of every candle we pour: a soft, creamy wax made from soybeans, "
        "chosen because it burns slowly and holds fragrance beautifully.",
        "illustration": "soy",
        "banner_color": "#EFE3CC",
        "banner_text": "dark",
        "body": "Soy wax starts as oil pressed from soybeans. The oil is hydrogenated — a process "
        "that turns it from liquid to solid at room temperature — giving us a plant-based wax "
        "with a gentle, creamy look.\n\n"
        "We use 100% soy wax because it suits the way we make things: slowly, by hand, poured "
        "into vessels we've cast ourselves. It melts at a lower temperature than many waxes, so "
        "the melt pool forms gently and carries scent across a room without rushing.",
        "points": [
            ("Renewable", "made from a crop that's replanted every year."),
            ("Slow, even burn", "a softer wax that melts steadily when the wick is well trimmed."),
            ("Creamy finish", "an opaque, natural look that sits well with matte plaster."),
            ("Made for containers", "its lower melting point is ideal for candles poured into a vessel."),
            ("Easy to clean up", "a drip on a table or fabric lifts with warm soapy water (just "
             "keep water off the plaster itself)."),
        ],
        "questions": [
            ("From soybean to candle",
             "Soybeans are harvested, cleaned and pressed for their oil. That oil is refined and "
             "hydrogenated so it sets solid at room temperature, then formed into soft flakes. In "
             "the studio we melt the flakes gently, stir in fragrance at the right temperature, and "
             "pour into our plaster vessels to set slowly overnight."),
            ("Soy vs. paraffin",
             "Paraffin is refined from petroleum; soy comes from a plant that is grown again every "
             "year. Paraffin is harder and throws scent strongly, while soy is softer, melts at a "
             "lower temperature and tends to burn more slowly. Both can burn cleanly with a "
             "well-sized, trimmed wick — we simply prefer soy for its natural origin and creamy look."),
            ("Why soy can “frost” (and why that's normal)",
             "Natural soy wax sometimes forms a thin white, crystal-like bloom on its surface or a "
             "few pale patches. It's simply the wax crystallising as it cools and settles. It doesn't "
             "change how the candle burns or smells, and it's one of the clearest signs you're "
             "burning real, natural soy."),
        ],
    },
    {
        "anchor": "plaster",
        "nav_label": "Plaster",
        "title": "Plaster",
        "intro": "Every vessel is cast, cured and finished by hand in our studio. It holds the "
        "candle, it never burns — and it stays with you long after the wax is gone.",
        "illustration": "plaster",
        "banner_color": "#E7E2DA",
        "banner_text": "dark",
        "body": "Plaster is a mineral: powdered gypsum mixed with water that sets hard like stone. "
        "It isn't a fuel and doesn't burn — it's the home for the wax and the part you'll keep.\n\n"
        "Because each piece is poured and finished by hand, no two are identical. You may spot a "
        "tiny air bubble, a soft shift in tone or a brushstroke that wandered. We think of those as "
        "the maker's fingerprint, not flaws.",
        "points": [
            ("Cast by hand", "one mould at a time."),
            ("Sealed for use with candles", "so the wax sits cleanly inside."),
            ("Reusable afterwards", "a dish, a pot, a home for little treasures."),
        ],
        "questions": [
            ("How we cast each piece",
             "We mix fine plaster with water by hand and pour it into our silicone moulds, tapping "
             "out as many air bubbles as we can. Once set, each piece is lifted out, left to cure and "
             "dry fully for several days, then smoothed, painted and sealed before any wax goes in."),
            ("Caring for plaster (keep dry, wipe gently)",
             "Plaster is porous, so keep it away from water and damp spots. Dust it with a soft dry "
             "brush or cloth, only when the candle is out and cool. Avoid cleaning sprays, and keep "
             "pieces out of strong direct sunlight to protect painted colours."),
            ("Reusing your vessel after the candle is gone",
             "Stop burning when about 1 cm of wax remains. Once completely cool, ease the leftover "
             "wax out with a wooden spoon and wipe the inside with a dry paper towel. Your vessel is "
             "ready for rings, keys, matches or a small potted plant — keep the plant in its own pot "
             "so no water touches the plaster."),
        ],
    },
    {
        "anchor": "wick",
        "nav_label": "Wick",
        "title": "Wick",
        "intro": "Small, but it runs the show. The wick draws melted wax up to the flame — and its "
        "size decides whether a candle burns clean and even.",
        "illustration": "wick",
        "banner_color": "#1E1610",
        "banner_text": "light",
        "body": "A candle flame doesn't burn the wick so much as the wax. Heat melts the wax into a "
        "pool, the wick soaks it up — the same way a paper towel draws up water — and the flame "
        "turns that liquid into vapour that burns.\n\n"
        "That's why size matters. Too small, and the flame can't melt wax to the edges, so the "
        "candle tunnels. Too large, and the flame grows, flickers and smokes. We test each vessel "
        "shape to match it with the right wick.",
        "cards_title": "About our wicks",
        "cards": [
            ("braid", "Braided cotton", "A soft, steady flame that curls slightly as it burns."),
            ("wood", "Wooden", "A wide, low flame with a gentle crackle, like a tiny hearth."),
            ("clock", "Sized per vessel",
             "Each shape is test-burned so the melt pool reaches the edge in a few hours."),
            ("scissors", "Trim to 5 mm",
             "Your part of the deal: a quick trim before each light keeps the flame calm."),
        ],
    },
    {
        "anchor": "fragrance",
        "nav_label": "Fragrance",
        "title": "Fragrance",
        "intro": "Scent is the part you feel first. We blend fragrance and essential oils with "
        "care, so a room fills softly rather than all at once.",
        "illustration": "fragrance",
        "banner_color": "#4E5A43",
        "banner_text": "light",
        "body": "Fragrance oil is stirred into the soy wax while it's warm and bonds with it as it "
        "sets. An unlit candle gives off a gentle scent from its surface. Once lit, the warm melt "
        "pool releases far more — that's why a candle smells strongest about an hour in.\n\n"
        "Every blend is measured carefully against the weight of the wax — enough to scent a room, "
        "never so much that it overwhelms or burns poorly.",
        "points": [
            ("Cold throw", "the scent of the candle at rest."),
            ("Hot throw", "the scent released from the melt pool while it burns."),
            ("Unscented", "for those who just want the glow."),
        ],
        "questions": [
            ("Hot throw vs. cold throw",
             "Cold throw is how a candle smells unlit, straight from the shelf. Hot throw is how it "
             "fills the room once the melt pool has formed — the warm wax lets more fragrance "
             "evaporate into the air. A candle with a lovely cold throw may smell softer when lit, "
             "and vice versa, which is why we test both."),
            ("Our scent families",
             "We group our blends into a few families so they're easy to choose between: warm & "
             "spiced, woody & smoky, fresh & herbal, soft floral, and sweet & cosy. Each product page "
             "shows the scents that candle comes in."),
            ("Fragrance safety",
             "Always burn scented candles in a well-ventilated room. If you're sensitive to scent, "
             "are pregnant or have pets, an unscented candle is a gentle choice — and you're welcome "
             "to ask us about the oils in any blend."),
        ],
    },
    {
        "anchor": "colour",
        "nav_label": "Colour",
        "title": "Colour",
        "intro": "A quiet, natural palette — plaster tones and soft wax colours chosen to match how "
        "each candle smells.",
        "illustration": "colour",
        "banner_color": "#F2EADF",
        "banner_text": "dark",
        "body": "We pair each colour with a feeling: warm terracotta for spiced blends, soft sage for "
        "herbal ones, creamy natural for the unscented. Wax is tinted with candle-safe dyes in small "
        "amounts, so the colour stays soft and the burn stays clean.\n\n"
        "Our painted collections — like the winter pieces — go bolder, with each detail added by "
        "brush. Every colour is mixed by hand, so expect gentle variation from batch to batch.",
        "swatches": [
            ("Raw Plaster", "#EFE9DF", "Unscented"),
            ("Oat", "#E8D9C3", "Soft floral"),
            ("Honey", "#D9B99A", "Sweet & cosy"),
            ("Terracotta", "#C4876A", "Warm & spiced"),
            ("Sage", "#A9B39A", "Fresh & herbal"),
            ("Pine", "#3E5A4A", "Woody & smoky"),
        ],
    },
]


def create_content(apps, schema_editor):
    get = lambda name: apps.get_model("ingredients", name)  # noqa: E731
    get("IngredientsPage").objects.get_or_create(pk=1)

    Chapter = get("Chapter")
    if Chapter.objects.exists():
        return

    for order, data in enumerate(CHAPTERS, start=1):
        data = dict(data)
        lists = {key: data.pop(key, []) for key in ["points", "questions", "cards", "swatches"]}
        chapter = Chapter.objects.create(order=order, **data)
        get("ChapterPoint").objects.bulk_create(
            get("ChapterPoint")(chapter=chapter, order=i, lead=lead, text=text)
            for i, (lead, text) in enumerate(lists["points"], start=1)
        )
        get("ChapterQuestion").objects.bulk_create(
            get("ChapterQuestion")(chapter=chapter, order=i, question=q, answer=a)
            for i, (q, a) in enumerate(lists["questions"], start=1)
        )
        get("ChapterCard").objects.bulk_create(
            get("ChapterCard")(chapter=chapter, order=i, icon=icon, title=title, text=text)
            for i, (icon, title, text) in enumerate(lists["cards"], start=1)
        )
        get("ChapterSwatch").objects.bulk_create(
            get("ChapterSwatch")(chapter=chapter, order=i, name=name, color=color, note=note)
            for i, (name, color, note) in enumerate(lists["swatches"], start=1)
        )


def remove_content(apps, schema_editor):
    apps.get_model("ingredients", "Chapter").objects.all().delete()
    apps.get_model("ingredients", "IngredientsPage").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ingredients", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_content, remove_content),
    ]
