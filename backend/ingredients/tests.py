from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from shop.testing import MediaTestMixin, make_image

from .models import Chapter, ChapterQuestion, ChapterSwatch, IngredientsPage


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


class IngredientsApiTests(MediaTestMixin, APITestCase):
    url = reverse("ingredients")

    def test_default_content_from_the_design(self):
        data = self.client.get(self.url).data
        self.assertEqual(data["hero_title"], "What's inside our candles")
        self.assertEqual(
            [c["anchor"] for c in data["chapters"]],
            ["soy", "plaster", "wick", "fragrance", "colour"],
        )
        soy, plaster, wick, fragrance, colour = data["chapters"]
        self.assertEqual(len(soy["paragraphs"]), 2)
        self.assertEqual(soy["points"][0], {"lead": "Renewable", "text": "made from a crop that's replanted every year."})
        self.assertEqual(len(soy["questions"]), 3)
        self.assertEqual(wick["cards_title"], "About our wicks")
        self.assertEqual(wick["cards"][0]["icon"], "braid")
        self.assertEqual(colour["swatches"][0], {"name": "Raw Plaster", "color": "#EFE9DF", "note": "Unscented"})
        self.assertEqual(wick["banner_text"], "light")
        self.assertIsNone(soy["banner_image"])
        self.assertNotIn("id", data)

    def test_default_content_has_no_placeholders_or_keepsakes(self):
        text = " ".join(strings(self.client.get(self.url).data)).lower()
        for word in ["[", "keepsake", "jar", "ifra", "phthalate"]:
            self.assertNotIn(word, text)

    def test_hidden_chapters_and_order(self):
        Chapter.objects.filter(anchor="wick").update(is_published=False)
        Chapter.objects.filter(anchor="colour").update(order=0)
        anchors = [c["anchor"] for c in self.client.get(self.url).data["chapters"]]
        self.assertEqual(anchors, ["colour", "soy", "plaster", "fragrance"])

    def test_paragraphs_split_on_blank_lines(self):
        chapter = Chapter.objects.get(anchor="soy")
        chapter.body = "First.\r\n\r\nSecond line one.\nSecond line two.\n\n\n"
        chapter.save()
        soy = self.client.get(self.url).data["chapters"][0]
        self.assertEqual(soy["paragraphs"], ["First.", "Second line one.\nSecond line two."])

    def test_photos_are_absolute_urls(self):
        page = IngredientsPage.load()
        page.hero_image = make_image("hero.png")
        page.save()
        chapter = Chapter.objects.get(anchor="soy")
        chapter.banner_image = make_image("soy.png")
        chapter.save()
        data = self.client.get(self.url).data
        self.assertTrue(data["hero_image"].startswith("http://testserver/media/ingredients/"))
        self.assertTrue(data["chapters"][0]["banner_image"].startswith("http://testserver/media/"))

    def test_query_count_is_constant(self):
        chapter = Chapter.objects.get(anchor="soy")
        for i in range(5):
            ChapterQuestion.objects.create(chapter=chapter, question=f"Q{i}", answer="a", order=10 + i)
        # page, chapters, points, questions, cards, swatches
        with self.assertNumQueries(6):
            self.client.get(self.url)

    def test_colours_are_validated(self):
        swatch = ChapterSwatch(chapter=Chapter.objects.first(), name="x", color="blue")
        with self.assertRaises(ValidationError):
            swatch.full_clean()


class IngredientsAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        self.client.force_login(user)

    def test_page_settings_is_a_single_form(self):
        response = self.client.get(reverse("admin:ingredients_ingredientspage_changelist"))
        self.assertRedirects(response, reverse("admin:ingredients_ingredientspage_change", args=[1]))

    def test_chapter_admin_with_inlines(self):
        changelist = self.client.get(reverse("admin:ingredients_chapter_changelist"))
        self.assertContains(changelist, "Soy wax")
        soy = Chapter.objects.get(anchor="soy")
        change = self.client.get(reverse("admin:ingredients_chapter_change", args=[soy.pk]))
        self.assertContains(change, "From soybean to candle")
        self.assertContains(change, "Renewable")
        self.assertContains(change, "No photo: the drawn illustration")
        self.assertEqual(self.client.get(reverse("admin:ingredients_chapter_add")).status_code, 200)
