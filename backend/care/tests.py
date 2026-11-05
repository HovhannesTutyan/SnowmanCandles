import io

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from shop.testing import MediaTestMixin, make_candle, make_image

from .models import FAQ, CarePage, CareTip


class CarePageApiTests(MediaTestMixin, APITestCase):
    url = reverse("care")

    def test_default_content_from_the_design(self):
        data = self.client.get(self.url).data
        self.assertEqual(data["hero_title"], "The art of a\nperfect burn")
        self.assertEqual(len(data["tips"]), 4)
        self.assertEqual(data["tips"][0]["title"], "Let the first burn go wide")
        self.assertEqual(len(data["rituals"]), 6)
        self.assertEqual(len(data["fragrance_tips"]), 3)
        self.assertEqual(len(data["faqs"]), 6)
        self.assertIsNone(data["hero_image"])
        self.assertIsNone(data["fragrance_product"])
        self.assertNotIn("id", data)

    def test_default_content_mentions_no_jars_keepsakes_or_placeholders(self):
        def strings(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for v in value.values():
                    yield from strings(v)
            elif isinstance(value, list):
                for v in value:
                    yield from strings(v)

        text = " ".join(strings(self.client.get(self.url).data)).lower()
        for word in ["jar", "keepsake", "figurine", "["]:
            self.assertNotIn(word, text)

    def test_lists_follow_the_admin_order(self):
        page = CarePage.load()
        page.faqs.all().delete()
        FAQ.objects.create(page=page, question="Second?", answer="b", order=2)
        FAQ.objects.create(page=page, question="First?", answer="a", order=1)
        faqs = self.client.get(self.url).data["faqs"]
        self.assertEqual([f["question"] for f in faqs], ["First?", "Second?"])
        self.assertEqual(faqs[0], {"question": "First?", "answer": "a"})

    def test_photos_and_featured_candle(self):
        page = CarePage.load()
        page.hero_image = make_image("hero.png")
        page.fragrance_product = make_candle(title="Holly Bauble Candle", price="24.00")
        page.save()

        data = self.client.get(self.url).data
        self.assertTrue(data["hero_image"].startswith("http://testserver/media/care/"))
        self.assertEqual(data["fragrance_product"]["slug"], "holly-bauble-candle")
        self.assertEqual(data["fragrance_product"]["price"], "24.00")

    def test_sold_out_featured_candle_is_hidden(self):
        page = CarePage.load()
        page.fragrance_product = make_candle(stock=0)
        page.save()
        self.assertIsNone(self.client.get(self.url).data["fragrance_product"])

    def test_query_count_is_constant(self):
        page = CarePage.load()
        for i in range(5):
            CareTip.objects.create(page=page, title=f"Extra {i}", text="x", order=10 + i)
        # load, page + candle, tips, rituals, fragrance tips, faqs
        with self.assertNumQueries(6):
            self.client.get(self.url)

    def test_is_a_singleton(self):
        CarePage(hero_title="Other").save()
        CarePage.load().delete()
        self.assertEqual(CarePage.objects.count(), 1)
        self.assertEqual(CarePage.load().hero_title, "Other")


class CarePageAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        self.client.force_login(user)

    def test_single_page_with_inline_lists(self):
        response = self.client.get(reverse("admin:care_carepage_changelist"))
        change_url = reverse("admin:care_carepage_change", args=[1])
        self.assertRedirects(response, change_url)

        page = self.client.get(change_url)
        self.assertContains(page, "Let the first burn go wide")
        self.assertContains(page, "How long should I burn my candle?")
        self.assertContains(page, "No photo: the page shows the candlelit scene")
        self.assertEqual(self.client.get(reverse("admin:care_carepage_add")).status_code, 403)


class SeedDemoCareTests(MediaTestMixin, TestCase):
    def test_seed_features_a_candle_on_the_care_page(self):
        call_command("seed_demo", stdout=io.StringIO())
        self.assertEqual(CarePage.load().fragrance_product.title, "Holly Bauble Candle")
