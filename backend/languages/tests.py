import io
import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from care.models import CarePage
from home.models import HomePageContent
from shop.models import Candle
from shop.testing import MediaTestMixin, make_candle

from .catalog import fill_all_from_catalog, translation_for
from .providers import TranslationError, translate
from .report import collect_missing, totals


class ApiLanguageTests(MediaTestMixin, APITestCase):
    def setUp(self):
        self.candle = make_candle(title="Carousel Candle", stock=3)
        self.candle.title_hy = "«Կարուսել» մոմ"
        self.candle.title_ru = "Свеча «Карусель»"
        self.candle.save()

    def get(self, lang=None):
        url = reverse("candle-detail", args=[self.candle.slug])
        return self.client.get(url, {"lang": lang} if lang else {})

    def test_answers_in_the_requested_language(self):
        self.assertEqual(self.get("hy").data["title"], "«Կարուսել» մոմ")
        self.assertEqual(self.get("ru").data["title"], "Свеча «Карусель»")
        response = self.get("en")
        self.assertEqual(response.data["title"], "Carousel Candle")
        self.assertEqual(response["Content-Language"], "en")

    def test_english_without_or_with_an_unknown_language(self):
        self.assertEqual(self.get().data["title"], "Carousel Candle")
        self.assertEqual(self.get("fr").data["title"], "Carousel Candle")

    def test_empty_translation_falls_back_to_english(self):
        # The description has no Armenian version.
        self.assertEqual(self.get("hy").data["description"], "A lovely candle.")

    def test_page_endpoints_do_not_list_every_language_column(self):
        data = self.client.get(reverse("site"), {"lang": "ru"}).data
        self.assertFalse([key for key in data if key.endswith(("_en", "_hy", "_ru"))])
        self.assertEqual(data["hero_title"], "Маленькие свечи для самых долгих ночей.")


class CatalogTests(MediaTestMixin, TestCase):
    def test_default_pages_are_translated_after_migrating(self):
        page = CarePage.objects.get(pk=1)
        self.assertEqual(page.hero_title_hy, "Կատարյալ այրման\nարվեստը")
        self.assertTrue(page.tips.first().title_ru)
        self.assertEqual(totals(collect_missing()), {"hy": 0, "ru": 0})

    def test_lookup_ignores_windows_line_endings(self):
        self.assertEqual(translation_for("Decorate\r\nwith light", "ru"), "Украшайте\nсветом")
        self.assertIsNone(translation_for("Something new", "hy"))

    def test_seed_demo_translates_the_demo_products(self):
        call_command("seed_demo", stdout=io.StringIO())
        candle = Candle.objects.get(title_en="Snowmen by the Campfire")
        self.assertEqual(candle.title_hy, "Ձնեմարդիկ խարույկի մոտ")
        self.assertEqual(candle.burn_time_ru, "~15 часов")
        self.assertEqual(totals(collect_missing()), {"hy": 0, "ru": 0})

    def test_filling_never_overwrites_a_translation(self):
        page = CarePage.objects.get(pk=1)
        page.hero_title_hy = "Իմ տարբերակը"
        page.save()
        fill_all_from_catalog()
        page.refresh_from_db()
        self.assertEqual(page.hero_title_hy, "Իմ տարբերակը")

    def test_new_rows_start_with_empty_translations(self):
        content = HomePageContent()
        self.assertEqual(content.hero_title_en, "Little candles for the longest nights.")
        self.assertEqual(content.hero_title_hy, "")


class AdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("boss", password="pw-12345678")
        self.client.force_login(self.user)
        self.candle = make_candle(title="Holly Bauble Candle")

    def test_change_form_has_a_box_per_language_and_english_is_required(self):
        response = self.client.get(reverse("admin:shop_candle_change", args=[self.candle.pk]))
        for name in ("title_en", "title_hy", "title_ru"):
            self.assertContains(response, f'name="{name}"')
        self.assertContains(response, 'id="languages-config"')
        self.assertContains(response, "languages/admin.js")

    def test_list_shows_which_items_need_translating(self):
        response = self.client.get(reverse("admin:shop_candle_changelist"))
        self.assertContains(response, "Missing: Armenian, Russian")

    def test_home_page_panel_and_overview_list_the_gaps(self):
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Translations")
        self.assertContains(response, "missing")
        response = self.client.get(reverse("languages_missing"))
        self.assertContains(response, "Holly Bauble Candle")
        self.assertContains(
            response, reverse("admin:shop_candle_change", args=[self.candle.pk])
        )

    def test_inline_rows_link_to_the_page_they_are_edited_on(self):
        tip = CarePage.objects.get(pk=1).tips.first()
        tip.text_ru = ""
        tip.save()
        response = self.client.get(reverse("languages_missing"))
        self.assertContains(response, "Care tip:")
        self.assertContains(response, reverse("admin:care_carepage_change", args=[1]))


class TranslateEndpointTests(TestCase):
    def setUp(self):
        self.url = reverse("languages_translate")
        user = get_user_model().objects.create_superuser("boss", password="pw-12345678")
        self.client.force_login(user)

    def post(self, payload):
        return self.client.post(self.url, json.dumps(payload), content_type="application/json")

    def test_staff_only(self):
        self.client.logout()
        response = self.post({"texts": ["Hello"]})
        self.assertEqual(response.status_code, 302)  # to the admin login

    def test_explains_that_translation_is_off(self):
        response = self.post({"texts": ["Hello"], "targets": ["hy"]})
        self.assertEqual(response.status_code, 502)
        self.assertIn("off", response.json()["error"])

    @mock.patch("languages.views.translate", side_effect=lambda texts, target: [f"{target}:{t}" for t in texts])
    def test_returns_a_translation_per_text_and_language(self, _translate):
        response = self.post({"texts": ["One", "Two"], "targets": ["hy", "ru"]})
        self.assertEqual(response.json(), {"hy": ["hy:One", "hy:Two"], "ru": ["ru:One", "ru:Two"]})

    def test_rejects_bad_requests(self):
        self.assertEqual(self.post({"nope": 1}).status_code, 400)
        self.assertEqual(self.post({"texts": [], "targets": ["hy"]}).status_code, 400)
        self.assertEqual(self.post({"texts": ["x"] * 500}).status_code, 400)


class ProviderTests(TestCase):
    @override_settings(TRANSLATION_PROVIDER="google", TRANSLATION_API_KEY="key")
    def test_google(self):
        body = json.dumps(
            {"data": {"translations": [{"translatedText": "Բարև"}, {"translatedText": "Մոմ"}]}}
        ).encode()
        response = mock.MagicMock()
        response.__enter__.return_value = io.BytesIO(body)
        with mock.patch("urllib.request.urlopen", return_value=response) as urlopen:
            self.assertEqual(translate(["Hello", "Candle"], "hy"), ["Բարև", "Մոմ"])
        sent = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(sent, {"q": ["Hello", "Candle"], "source": "en", "target": "hy", "format": "text"})

    @override_settings(TRANSLATION_PROVIDER="google", TRANSLATION_API_KEY="key")
    def test_incomplete_answer_is_an_error(self):
        body = json.dumps({"data": {"translations": [{"translatedText": "Բարև"}]}}).encode()
        response = mock.MagicMock()
        response.__enter__.return_value = io.BytesIO(body)
        with mock.patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(TranslationError):
                translate(["Hello", "Candle"], "hy")

    @override_settings(TRANSLATION_PROVIDER="claude", TRANSLATION_API_KEY="")
    def test_off_without_a_key(self):
        with self.assertRaisesMessage(TranslationError, "off"):
            translate(["Hello"], "ru")
