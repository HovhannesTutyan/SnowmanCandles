import io

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from shop.models import Candle
from shop.testing import MediaTestMixin, make_candle, make_collection, make_image

from .models import HeroSlide, HomePageContent


class HeroSlideValidationTests(MediaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.candle = make_candle()
        cls.collection = make_collection()

    def test_cannot_link_both_candle_and_collection(self):
        slide = HeroSlide(title="Both", candle=self.candle, collection=self.collection)
        with self.assertRaises(ValidationError) as ctx:
            slide.full_clean()
        self.assertIn("not both", str(ctx.exception))

    def test_requires_image_or_link(self):
        slide = HeroSlide(title="Empty")
        with self.assertRaises(ValidationError) as ctx:
            slide.full_clean()
        self.assertIn("image", ctx.exception.message_dict)

    def test_valid_combinations(self):
        HeroSlide(title="Own image", image="slides/x.png").full_clean()
        HeroSlide(title="Candle", candle=self.candle).full_clean()
        HeroSlide(title="Collection", collection=self.collection).full_clean()


class HomeApiTests(MediaTestMixin, APITestCase):
    url = reverse("home")

    def test_slide_image_fallback_and_link(self):
        candle = make_candle(title="Linked Candle", product_type="set")
        collection = make_collection(title="Linked Set")
        HeroSlide.objects.create(title="Own", image=make_image(), order=1)
        HeroSlide.objects.create(title="From candle", candle=candle, order=2)
        HeroSlide.objects.create(title="From collection", collection=collection, order=3)

        own, from_candle, from_collection = self.client.get(self.url).data["slides"]

        self.assertTrue(own["image"].startswith("http://testserver/media/slides/"))
        self.assertIsNone(own["link"])
        self.assertEqual(set(own), {"id", "title", "subtitle", "image", "button_text", "link"})
        self.assertEqual(from_candle["image"], "http://testserver" + candle.image.url)
        self.assertEqual(
            from_candle["link"],
            {"type": "candle", "slug": "linked-candle", "price": "12.50",
             "product_type_label": "Candle set"},
        )
        self.assertEqual(from_collection["image"], "http://testserver" + collection.image.url)
        self.assertEqual(
            from_collection["link"],
            {"type": "collection", "slug": "linked-set", "price": "39.99",
             "product_type_label": "Collection"},
        )

    def test_inactive_slides_hidden_and_ordered(self):
        candle = make_candle()
        HeroSlide.objects.create(title="Third", candle=candle, order=3)
        HeroSlide.objects.create(title="First", candle=candle, order=1)
        HeroSlide.objects.create(title="Hidden", candle=candle, order=2, is_active=False)

        slides = self.client.get(self.url).data["slides"]
        self.assertEqual([s["title"] for s in slides], ["First", "Third"])

    def test_featured_items_filtered_and_ordered(self):
        make_candle(title="Second", is_featured=True, featured_order=2)
        make_candle(title="First", is_featured=True, featured_order=1)
        make_candle(title="Sold out", is_featured=True, featured_order=0, stock=0)
        make_candle(title="Not featured")
        make_collection(title="Set B", is_featured=True, featured_order=5)
        make_collection(title="Set A", is_featured=True, featured_order=5)  # newer wins a tie
        make_collection(title="Sold out set", is_featured=True, stock=0)

        data = self.client.get(self.url).data
        self.assertEqual([c["title"] for c in data["featured_candles"]], ["First", "Second"])
        self.assertEqual([c["title"] for c in data["featured_collections"]], ["Set A", "Set B"])
        self.assertIn("candle_count", data["featured_collections"][0])
        self.assertEqual(data["featured_candles"][0]["price"], "12.50")

    def test_featured_items_limited_to_8(self):
        for i in range(10):
            make_candle(title=f"Candle {i}", is_featured=True, featured_order=i)
            make_collection(title=f"Set {i}", is_featured=True, featured_order=i)

        data = self.client.get(self.url).data
        self.assertEqual(len(data["featured_candles"]), 8)
        self.assertEqual(len(data["featured_collections"]), 8)
        self.assertEqual(data["featured_candles"][0]["title"], "Candle 0")

    def test_empty_homepage(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["slides"], [])
        self.assertEqual(data["featured_candles"], [])
        self.assertEqual(data["featured_collections"], [])
        self.assertNotIn("content", data)  # site texts come from /api/site/

    def test_query_count_does_not_grow_with_items(self):
        HomePageContent.load()
        for i in range(3):
            candle = make_candle(title=f"C{i}", is_featured=True)
            collection = make_collection(title=f"S{i}", is_featured=True)
            HeroSlide.objects.create(title=f"Slide C{i}", candle=candle)
            HeroSlide.objects.create(title=f"Slide S{i}", collection=collection)

        with self.assertNumQueries(3):  # slides, featured candles, featured collections
            self.client.get(self.url)


class HeroSlideAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        self.client.force_login(user)
        self.slide = HeroSlide.objects.create(title="Hero", candle=make_candle(title="Linked"))

    def test_admin_pages_render(self):
        changelist = self.client.get(reverse("admin:home_heroslide_changelist"))
        self.assertContains(changelist, "Candle: Linked")
        change = self.client.get(reverse("admin:home_heroslide_change", args=[self.slide.pk]))
        self.assertContains(change, "from the linked item")
        self.assertEqual(self.client.get(reverse("admin:home_heroslide_add")).status_code, 200)

    def test_autocomplete_endpoints_work(self):
        for field in ["candle", "collection"]:
            with self.subTest(field=field):
                response = self.client.get(
                    reverse("admin:autocomplete"),
                    {"app_label": "home", "model_name": "heroslide",
                     "field_name": field, "term": "Lin"},
                )
                self.assertEqual(response.status_code, 200)


class HomePageContentTests(MediaTestMixin, APITestCase):
    def test_is_a_singleton(self):
        first = HomePageContent.load()
        HomePageContent(studio_name="Another").save()
        self.assertEqual(HomePageContent.objects.count(), 1)
        first.refresh_from_db()
        self.assertEqual(first.studio_name, "Another")

    def test_cannot_be_deleted(self):
        HomePageContent.load().delete()
        self.assertEqual(HomePageContent.objects.count(), 1)

    def test_site_endpoint_includes_product_page_texts(self):
        data = self.client.get(reverse("site")).data
        self.assertEqual(data["ships_in"], "3–5 days")
        self.assertIn("Trim the wick", data["care_text"])
        self.assertTrue(data["shipping_text"])
        self.assertEqual(data["story_title"], "Hours of small brushstrokes in every one.")
        self.assertTrue(data["price_note"])

    def test_content_in_site_api(self):
        content = HomePageContent.load()
        content.ticker_messages = "First\n\n  Second  \n"
        content.studio_name = "Glow Studio"
        content.made_before_image = make_image("before.png")
        content.save()

        data = self.client.get(reverse("site")).data
        self.assertEqual(data["studio_name"], "Glow Studio")
        self.assertEqual(data["ticker_messages"], ["First", "Second"])
        self.assertTrue(
            data["images"]["made_before"].startswith("http://testserver/media/homepage/")
        )
        self.assertIsNone(data["images"]["made_after"])  # frontend falls back to the design
        self.assertNotIn("made_before_image", data)
        self.assertNotIn("id", data)

    def test_invalid_colour_rejected(self):
        content = HomePageContent.load()
        content.accent_color = "red"
        with self.assertRaises(ValidationError):
            content.full_clean()


class HomePageContentAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        self.client.force_login(user)

    def test_changelist_redirects_to_the_single_form(self):
        response = self.client.get(reverse("admin:home_homepagecontent_changelist"))
        self.assertRedirects(response, reverse("admin:home_homepagecontent_change", args=[1]))
        page = self.client.get(reverse("admin:home_homepagecontent_change", args=[1]))
        self.assertContains(page, "Using the image from the original design.")

    def test_no_add_or_delete(self):
        self.assertEqual(
            self.client.get(reverse("admin:home_homepagecontent_add")).status_code, 403
        )
        HomePageContent.load()
        self.assertEqual(
            self.client.get(
                reverse("admin:home_homepagecontent_delete", args=[1])
            ).status_code,
            403,
        )


class SeedDemoCommandTests(MediaTestMixin, TestCase):
    def test_seeds_design_content_once(self):
        call_command("seed_demo", stdout=io.StringIO())
        call_command("seed_demo", stdout=io.StringIO())  # second run changes nothing

        self.assertEqual(Candle.objects.count(), 6)
        roadster = Candle.objects.get(title="Vintage Roadster Candle")
        self.assertEqual(roadster.flame, {"x": 47.6, "y": 86.5})
        snowmen = Candle.objects.get(title="Snowmen by the Campfire")
        views = list(snowmen.showcase_views.all())
        self.assertEqual([v.short_label for v in views], ["Front", "Angle", "Back", "Side", "Top", "Bottom"])
        self.assertEqual(views[4].group, "top")
        self.assertEqual(roadster.scents.count(), 3)
        self.assertTrue(roadster.burn_time)
        self.assertEqual(Candle.objects.filter(is_featured=True).count(), 6)
        self.assertEqual(HeroSlide.objects.count(), 4)
        campfire = HeroSlide.objects.first().candle
        self.assertEqual(campfire.title, "Snowmen by the Campfire")
        self.assertEqual(campfire.product_type, "set")
        self.assertEqual(
            set(Candle.objects.values_list("product_type", flat=True)),
            {"candle", "set"},
        )


    def test_seed_does_not_overwrite_admin_edits(self):
        call_command("seed_demo", stdout=io.StringIO())
        roadster = Candle.objects.get(title="Vintage Roadster Candle")
        roadster.burn_time = "40 hours"
        roadster.save()
        call_command("seed_demo", stdout=io.StringIO())
        roadster.refresh_from_db()
        self.assertEqual(roadster.burn_time, "40 hours")
