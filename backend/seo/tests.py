import html as html_lib
import json
from xml.etree import ElementTree
import re
import shutil
import tempfile
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from care.models import FAQ, CarePage
from home.models import HomePageContent
from shop.models import ProductType
from shop.testing import MediaTestMixin, make_candle, make_collection

from .models import SeoSettings
from .pages import clip, format_price, localize, split_locale

INDEX = """<!doctype html>
<html lang="hy-AM">
  <head>
    <meta charset="UTF-8" />
    <meta name="description" content="Placeholder." />
    <title>Candle Shop</title>
    <script type="module" src="/assets/index.js"></script>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
"""


class AddressTests(TestCase):
    def test_language_prefixes(self):
        self.assertEqual(split_locale("/"), ("hy", "/"))
        self.assertEqual(split_locale("/en"), ("en", "/"))
        self.assertEqual(split_locale("/ru/decorate/"), ("ru", "/decorate"))
        self.assertEqual(split_locale("/english-tea"), ("hy", "/english-tea"))
        self.assertEqual(localize("/", "en"), "/en")
        self.assertEqual(localize("/candle-care", "hy"), "/candle-care")

    def test_helpers(self):
        self.assertEqual(clip("word " * 50, 20), "word word word word…")
        self.assertEqual(format_price(Decimal("1234.5"), "USD"), "$1,234.50")
        self.assertEqual(format_price(Decimal("12000"), "AMD"), "12,000 ֏")


@override_settings(SITE_URL="https://shop.example")
class PageTests(MediaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        content = HomePageContent.load()
        content.studio_name = "Test Studio"
        content.instagram_handle = "@teststudio"
        content.save()
        cls.candle = make_candle(
            title="Holly Candle",
            title_hy="Սուրբծննդյան մոմ",
            title_ru="Свеча с остролистом",
            is_featured=True,
            product_type=ProductType.CANDLE,
        )
        cls.candle.description_en = "A <b>bold</b> candle. " + "Painted by hand. " * 20
        cls.candle.save()
        cls.sold_out = make_candle(title="Gone Candle", stock=0)
        cls.collection = make_collection(title="Winter Set")
        cls.collection.candles.add(cls.candle)

    def setUp(self):
        self.dist = Path(tempfile.mkdtemp())
        (self.dist / "index.html").write_text(INDEX, encoding="utf-8")
        self.settings_override = override_settings(FRONTEND_DIST=self.dist)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.dist, ignore_errors=True)

    def get(self, url, status=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status, url)
        return response.content.decode()

    def json_ld(self, html):
        match = re.search(r'<script data-ssr type="application/ld\+json">(.*?)</script>', html)
        self.assertIsNotNone(match)
        return {item["@type"]: item for item in json.loads(match[1])["@graph"]}

    def test_one_title_and_description_in_the_page_language(self):
        html = self.get("/ru/candles/" + self.candle.slug)
        self.assertIn('<html lang="ru-RU"', html)
        self.assertEqual(html.count("<title"), 1)
        self.assertIn("<title data-ssr>Свеча с остролистом — Test Studio</title>", html)
        self.assertEqual(html.count('name="description"'), 1)
        self.assertNotIn("Placeholder.", html)

    def test_canonical_and_language_versions(self):
        html = self.get("/en/candles/" + self.candle.slug + "/")
        url = f"https://shop.example/en/candles/{self.candle.slug}"
        self.assertIn(f'<link data-ssr rel="canonical" href="{url}" />', html)
        for lang, prefix in [("hy", ""), ("en", "/en"), ("ru", "/ru"), ("x-default", "")]:
            self.assertIn(
                f'hreflang="{lang}" href="https://shop.example{prefix}/candles/{self.candle.slug}"',
                html,
            )

    def test_preview_tags_for_shared_links(self):
        html = self.get("/en/candles/" + self.candle.slug)
        self.assertIn('property="og:type" content="product"', html)
        self.assertIn('property="og:title" content="Holly Candle — Test Studio"', html)
        self.assertRegex(html, r'property="og:image" content="https://shop\.example/media/candles/')
        self.assertIn('property="og:locale" content="en_US"', html)
        self.assertIn('property="product:price:amount" content="12.50"', html)

    def test_description_is_shortened_and_escaped(self):
        html = self.get("/en/candles/" + self.candle.slug)
        description = re.search(r'<meta data-ssr name="description" content="([^"]*)"', html)[1]
        self.assertLessEqual(len(html_lib.unescape(description)), 160)
        self.assertTrue(description.endswith("…"))
        self.assertIn("&lt;b&gt;bold&lt;/b&gt;", description)
        self.assertNotIn("<b>bold</b>", html)

    def test_product_structured_data(self):
        data = self.json_ld(self.get("/candles/" + self.candle.slug))
        product = data["Product"]
        self.assertEqual(product["name"], "Սուրբծննդյան մոմ")
        self.assertEqual(product["brand"]["name"], "Test Studio")
        self.assertEqual(product["offers"]["price"], "12.50")
        self.assertEqual(product["offers"]["priceCurrency"], "USD")
        self.assertEqual(product["offers"]["availability"], "https://schema.org/InStock")
        shipping = product["offers"]["shippingDetails"]
        self.assertEqual(shipping["shippingRate"]["value"], 0)
        self.assertEqual(shipping["shippingDestination"]["addressCountry"], "AM")
        self.assertEqual(shipping["deliveryTime"]["transitTime"]["maxValue"], 2)
        self.assertTrue(product["image"][0].startswith("https://shop.example/media/"))
        self.assertEqual(data["OnlineStore"]["sameAs"], ["https://www.instagram.com/teststudio/"])
        self.assertEqual(len(data["BreadcrumbList"]["itemListElement"]), 2)

        sold_out = self.json_ld(self.get("/en/candles/" + self.sold_out.slug))["Product"]
        self.assertEqual(sold_out["offers"]["availability"], "https://schema.org/OutOfStock")

    def test_structured_data_cannot_close_the_script_tag(self):
        self.candle.title_en = "Candle </script><script>alert(1)</script>"
        self.candle.save()
        html = self.get("/en/candles/" + self.candle.slug)
        self.assertNotIn("<script>alert(1)", html)
        self.assertEqual(self.json_ld(html)["Product"]["name"], self.candle.title_en)

    def test_page_text_is_in_the_html(self):
        html = self.get("/en")
        root = html[html.index('<div id="root">'):]
        self.assertIn("<h1>", root)
        self.assertIn(f'href="/en/candles/{self.candle.slug}"', root)
        self.assertIn(f'href="/en/collections/{self.collection.slug}"', root)
        self.assertIn("$12.50", root)

        product = self.get("/en/collections/" + self.collection.slug)
        self.assertIn("<h1>Winter Set</h1>", product)
        self.assertIn("Holly Candle", product)  # what the set includes

    def test_care_page_questions(self):
        page = CarePage.load()
        FAQ.objects.create(page=page, question="Can I reuse it?", answer="Yes, refill it.")
        html = self.get("/en/candle-care")
        self.assertIn("Candle Care &amp; Tips — Test Studio", html)
        faq = self.json_ld(html)["FAQPage"]
        self.assertIn({"@type": "Question", "name": "Can I reuse it?",
                       "acceptedAnswer": {"@type": "Answer", "text": "Yes, refill it."}},
                      faq["mainEntity"])
        self.assertIn("<h3>Can I reuse it?</h3>", html)

    def test_texts_from_the_admin_win(self):
        seo = SeoSettings.load()
        seo.home_title_en = "Handmade candles in Yerevan"
        seo.home_description_ru = "Свечи ручной работы в Ереване."
        seo.save()
        self.candle.seo_title_en = "Holly candle gift"
        self.candle.save()

        self.assertIn("<title data-ssr>Handmade candles in Yerevan</title>", self.get("/en"))
        self.assertIn('content="Свечи ручной работы в Ереване."', self.get("/ru"))
        self.assertIn("<title data-ssr>Holly candle gift</title>",
                      self.get("/en/candles/" + self.candle.slug))
        # An empty Armenian box gives the automatic Armenian text, not the English one.
        self.assertIn("<title data-ssr>Test Studio — ձեռքով", self.get("/"))

    def test_basket_and_checkout_are_kept_out_of_search(self):
        for url in ["/basket", "/en/checkout"]:
            html = self.get(url)
            self.assertIn('name="robots" content="noindex, follow"', html)
            self.assertNotIn('rel="canonical"', html)

    def test_missing_pages_are_a_real_404(self):
        for url in ["/en/candles/no-such-candle", "/ru/collections/nope", "/no-such-page"]:
            html = self.get(url, status=404)
            self.assertIn('name="robots" content="noindex, follow"', html)
            self.assertIn('<div id="root">', html)  # the app still loads and shows its page

    def test_other_pages(self):
        for url, title in [
            ("/en/ingredients", "What&#x27;s inside our candles — Test Studio"),
            ("/ru/decorate", "Декор со свечами — Test Studio"),
        ]:
            self.assertIn(f"<title data-ssr>{title}</title>", self.get(url))


class AdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pass")
        self.client.force_login(user)

    def test_settings_page_shows_the_automatic_texts(self):
        response = self.client.get("/admin/seo/seosettings/", follow=True)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('name="home_title_hy"', html)
        self.assertIn("ձեռքով նկարված մոմեր", html)  # grey placeholder text
        self.assertIn("Уход за свечами и советы", html)

    def test_product_page_has_the_seo_section(self):
        candle = make_candle(title="Admin Candle")
        html = self.client.get(f"/admin/shop/candle/{candle.pk}/change/").content.decode()
        self.assertIn("Search engines (SEO)", html)
        self.assertIn('placeholder="Admin Candle — ', html)


@override_settings(SITE_URL="https://shop.example")
class RobotsAndSitemapTests(MediaTestMixin, TestCase):
    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        text = response.content.decode()
        self.assertIn("Disallow: /admin/", text)
        self.assertNotIn("/api/", text)  # Google needs the API to show the React pages
        self.assertIn("Sitemap: https://shop.example/sitemap.xml", text)

    def test_sitemap_lists_every_page_in_every_language(self):
        candle = make_candle(title="Map Candle")
        collection = make_collection(title="Map Set")
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml; charset=utf-8")
        xml = response.content.decode()
        self.assertTrue(xml.startswith('<?xml version="1.0"'))
        for path in ["", "/candle-care", "/ingredients", "/decorate",
                     f"/candles/{candle.slug}", f"/collections/{collection.slug}"]:
            for prefix in ["", "/en", "/ru"]:
                loc = f"https://shop.example{prefix}{path}" if prefix or path else "https://shop.example/"
                self.assertIn(f"<loc>{loc}</loc>", xml)
        self.assertIn('hreflang="x-default" href="https://shop.example/candles/map-candle"', xml)
        self.assertIn("<image:loc>https://shop.example/media/candles/", xml)
        self.assertNotIn("basket", xml)
        self.assertNotIn("checkout", xml)
        root = ElementTree.fromstring(response.content)
        self.assertEqual(len(root), 6 * 3)
