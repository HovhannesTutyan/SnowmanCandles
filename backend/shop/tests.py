from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Candle, CandleImage, CandleShowcaseView, Scent
from .testing import MediaTestMixin, make_candle, make_collection, make_image


class SlugTests(MediaTestMixin, TestCase):
    def test_slug_generated_from_title(self):
        self.assertEqual(make_candle(title="Vanilla Dream").slug, "vanilla-dream")

    def test_duplicate_titles_get_numbered_suffixes(self):
        slugs = [make_candle(title="Rose Garden").slug for _ in range(3)]
        self.assertEqual(slugs, ["rose-garden", "rose-garden-2", "rose-garden-3"])

    def test_explicit_slug_is_kept(self):
        self.assertEqual(make_candle(slug="custom-slug").slug, "custom-slug")

    def test_slug_not_changed_on_resave(self):
        candle = make_candle(title="Cedar")
        candle.title = "Cedar Renamed"
        candle.save()
        self.assertEqual(candle.slug, "cedar")

    def test_slugs_are_unique_per_model(self):
        # A candle and a collection may share a slug; they live at different endpoints.
        self.assertEqual(make_candle(title="Lavender").slug, "lavender")
        self.assertEqual(make_collection(title="Lavender").slug, "lavender")


class AvailabilityTests(MediaTestMixin, TestCase):
    def test_is_available_when_in_stock(self):
        self.assertTrue(make_candle(stock=3).is_available)

    def test_not_available_when_stock_is_zero(self):
        self.assertFalse(make_candle(stock=0).is_available)
        self.assertFalse(make_collection(stock=0).is_available)


class PriceValidationTests(MediaTestMixin, TestCase):
    def test_zero_and_negative_prices_fail_validation(self):
        for price in ["0", "0.00", "-1.00"]:
            candle = Candle(title="Bad", description="x", image="x.png", price=Decimal(price))
            with self.subTest(price=price), self.assertRaises(ValidationError) as ctx:
                candle.full_clean()
            self.assertIn("price", ctx.exception.message_dict)

    def test_positive_price_passes_validation(self):
        candle = Candle(title="Good", description="x", image="x.png", price=Decimal("0.01"))
        candle.full_clean()  # does not raise

    def test_database_rejects_non_positive_price(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_candle(price="0")


class CandleApiTests(MediaTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cheap = make_candle(title="Cheap", price="5.00", stock=10)
        cls.mid = make_candle(title="Mid", price="15.50", stock=0)
        cls.pricey = make_candle(title="Pricey", price="40.00", stock=2)
        cls.url = reverse("candle-list")

    def titles(self, response):
        return [item["title"] for item in response.data["results"]]

    def test_list_returns_paginated_items(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertIn("results", response.data)

    def test_list_item_shape(self):
        response = self.client.get(self.url, {"ordering": "price"})
        item = response.data["results"][0]
        self.assertEqual(item["price"], "5.00")
        self.assertEqual(item["stock"], 10)
        self.assertIs(item["is_available"], True)
        self.assertTrue(item["image"].startswith("http://testserver/media/candles/"))

    def test_default_ordering_newest_first(self):
        response = self.client.get(self.url)
        self.assertEqual(self.titles(response), ["Pricey", "Mid", "Cheap"])

    def test_ordering_by_price(self):
        self.assertEqual(
            self.titles(self.client.get(self.url, {"ordering": "price"})),
            ["Cheap", "Mid", "Pricey"],
        )
        self.assertEqual(
            self.titles(self.client.get(self.url, {"ordering": "-price"})),
            ["Pricey", "Mid", "Cheap"],
        )

    def test_available_filter(self):
        response = self.client.get(self.url, {"available": "true"})
        self.assertCountEqual(self.titles(response), ["Cheap", "Pricey"])

    def test_price_filters(self):
        response = self.client.get(self.url, {"min_price": "10", "max_price": "20"})
        self.assertEqual(self.titles(response), ["Mid"])
        response = self.client.get(self.url, {"min_price": "15.50"})
        self.assertCountEqual(self.titles(response), ["Mid", "Pricey"])

    def test_combined_filters(self):
        response = self.client.get(self.url, {"available": "true", "min_price": "10"})
        self.assertEqual(self.titles(response), ["Pricey"])

    def test_invalid_filter_values_return_400(self):
        for params in [{"min_price": "abc"}, {"max_price": "-5"}, {"available": "maybe"}]:
            with self.subTest(params=params):
                self.assertEqual(self.client.get(self.url, params).status_code, 400)

    def test_detail_by_slug(self):
        response = self.client.get(reverse("candle-detail", args=[self.mid.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Mid")
        self.assertIs(response.data["is_available"], False)

    def test_detail_404(self):
        response = self.client.get(reverse("candle-detail", args=["nope"]))
        self.assertEqual(response.status_code, 404)

    def test_api_is_read_only(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 405)

    def test_page_size_is_12(self):
        for i in range(12):
            make_candle(title=f"Extra {i}")
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["results"]), 12)
        self.assertIsNotNone(response.data["next"])


class CollectionApiTests(MediaTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.candle_a = make_candle(title="Amber", price="10.00", stock=0)
        cls.candle_b = make_candle(title="Birch", price="12.00")
        cls.full = make_collection(title="Full Set", price="50.00", stock=3)
        cls.full.candles.set([cls.candle_a, cls.candle_b])
        cls.empty = make_collection(title="Sold Out Set", price="20.00", stock=0)
        cls.url = reverse("collection-list")

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        item = next(r for r in response.data["results"] if r["slug"] == "full-set")
        self.assertEqual(item["price"], "50.00")
        self.assertEqual(item["candle_count"], 2)
        self.assertTrue(item["image"].startswith("http://testserver/media/collections/"))

    def test_collection_stock_independent_of_candles(self):
        # A candle inside is out of stock, but the collection still has its own stock.
        response = self.client.get(reverse("collection-detail", args=["full-set"]))
        self.assertIs(response.data["is_available"], True)

    def test_filters(self):
        response = self.client.get(self.url, {"available": "true"})
        self.assertEqual([r["title"] for r in response.data["results"]], ["Full Set"])
        response = self.client.get(self.url, {"max_price": "30"})
        self.assertEqual([r["title"] for r in response.data["results"]], ["Sold Out Set"])

    def test_detail_includes_nested_candles(self):
        response = self.client.get(reverse("collection-detail", args=["full-set"]))
        self.assertEqual(response.status_code, 200)
        candles = sorted(response.data["candles"], key=lambda c: c["title"])
        self.assertEqual([c["slug"] for c in candles], ["amber", "birch"])
        self.assertEqual(
            set(candles[0]),
            {"title", "slug", "image", "price", "tint", "product_type_label", "is_available"},
        )
        self.assertEqual(candles[0]["price"], "10.00")
        self.assertTrue(candles[0]["image"].startswith("http://testserver/media/candles/"))


class AdminTests(MediaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        cls.admin_user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        cls.in_stock = make_candle(title="Plenty", stock=20)
        cls.low = make_candle(title="Few", stock=3)
        cls.out = make_candle(title="None Left", stock=0)
        cls.collection = make_collection(title="Bundle")
        cls.collection.candles.set([cls.in_stock, cls.low])

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_changelist_and_change_pages_render(self):
        for name, obj in [("candle", self.in_stock), ("collection", self.collection)]:
            with self.subTest(model=name):
                changelist = self.client.get(reverse(f"admin:shop_{name}_changelist"))
                self.assertEqual(changelist.status_code, 200)
                change = self.client.get(reverse(f"admin:shop_{name}_change", args=[obj.pk]))
                self.assertEqual(change.status_code, 200)
                self.assertContains(change, obj.image.url)  # large preview

    def test_availability_labels_and_filter(self):
        url = reverse("admin:shop_candle_changelist")
        response = self.client.get(url)
        for label in ["In stock", "Low stock", "Out of stock"]:
            self.assertContains(response, label)
        response = self.client.get(url, {"availability": "low_stock"})
        self.assertEqual([c.title for c in response.context["cl"].result_list], ["Few"])

    def test_mark_out_of_stock_action(self):
        self.client.post(
            reverse("admin:shop_candle_changelist"),
            {"action": "mark_out_of_stock", "_selected_action": [self.in_stock.pk, self.low.pk]},
        )
        self.assertEqual(Candle.objects.filter(stock=0).count(), 3)

    def test_add_and_remove_featured_actions(self):
        url = reverse("admin:shop_candle_changelist")
        ids = [self.in_stock.pk, self.low.pk]
        self.client.post(url, {"action": "add_to_featured", "_selected_action": ids})
        self.assertEqual(Candle.objects.filter(is_featured=True).count(), 2)
        self.client.post(url, {"action": "remove_from_featured", "_selected_action": ids})
        self.assertEqual(Candle.objects.filter(is_featured=True).count(), 0)


class FeaturedFilterTests(MediaTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        make_candle(title="Star", is_featured=True)
        make_candle(title="Plain")
        make_collection(title="Star Set", is_featured=True)
        make_collection(title="Plain Set")

    def titles(self, url, params):
        return [r["title"] for r in self.client.get(url, params).data["results"]]

    def test_featured_filter_on_candles_and_collections(self):
        self.assertEqual(self.titles(reverse("candle-list"), {"featured": "true"}), ["Star"])
        self.assertEqual(self.titles(reverse("candle-list"), {"featured": "false"}), ["Plain"])
        self.assertEqual(
            self.titles(reverse("collection-list"), {"featured": "true"}), ["Star Set"]
        )

    def test_is_featured_in_serializer(self):
        response = self.client.get(reverse("candle-list"), {"featured": "true"})
        self.assertIs(response.data["results"][0]["is_featured"], True)

    def test_invalid_featured_value_returns_400(self):
        response = self.client.get(reverse("candle-list"), {"featured": "sometimes"})
        self.assertEqual(response.status_code, 400)


class ProductTypeTests(MediaTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        make_candle(title="Car Candle")
        make_candle(title="Campfire Set", product_type="set", tint="#F3E1DB")
        make_collection(title="Winter Set")

    def test_type_filter(self):
        response = self.client.get(reverse("candle-list"), {"type": "set"})
        self.assertEqual([r["title"] for r in response.data["results"]], ["Campfire Set"])
        item = response.data["results"][0]
        self.assertEqual(item["product_type"], "set")
        self.assertEqual(item["product_type_label"], "Candle set")
        self.assertEqual(item["tint"], "#F3E1DB")

        response = self.client.get(reverse("candle-list"), {"type": "candle"})
        self.assertEqual([r["title"] for r in response.data["results"]], ["Car Candle"])
        self.assertEqual(response.data["results"][0]["product_type_label"], "Single candle")

    def test_removed_types_are_rejected(self):
        for old_type in ["keepsake_jar", "figurine"]:
            with self.subTest(type=old_type):
                response = self.client.get(reverse("candle-list"), {"type": old_type})
                self.assertEqual(response.status_code, 400)
                candle = Candle(title="x", description="x", image="x.png",
                                price=Decimal("1"), product_type=old_type)
                with self.assertRaises(ValidationError):
                    candle.full_clean()

    def test_invalid_type_returns_400(self):
        response = self.client.get(reverse("candle-list"), {"type": "lamp"})
        self.assertEqual(response.status_code, 400)

    def test_collections_have_the_same_keys(self):
        item = self.client.get(reverse("collection-list")).data["results"][0]
        self.assertEqual(item["product_type"], "collection")
        self.assertEqual(item["product_type_label"], "Collection")
        self.assertEqual(item["tint"], "#E4ECDC")

    def test_invalid_tint_rejected(self):
        candle = Candle(
            title="x", description="x", image="x.png", price=Decimal("1"), tint="green"
        )
        with self.assertRaises(ValidationError) as ctx:
            candle.full_clean()
        self.assertIn("tint", ctx.exception.message_dict)


class ProductPageApiTests(MediaTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.roadster = make_candle(
            title="Roadster",
            burn_time="~25 hours",
            size="14 × 7 × 8 cm",
            details="Soy wax, cotton wick.",
            story_title="Brushstrokes",
            story_text="Painted by hand.",
            flame_x=Decimal("47.6"),
            flame_y=Decimal("86.5"),
        )
        pine = Scent.objects.create(name="Pine", order=2)
        unscented = Scent.objects.create(name="Unscented", order=1)
        cls.roadster.scents.set([pine, unscented])
        CandleImage.objects.create(
            candle=cls.roadster, image=make_image("wheel.png"), label="Wheel detail", order=2
        )
        CandleImage.objects.create(
            candle=cls.roadster, image=make_image("grille.png"), label="Grille detail", order=1
        )

    def test_detail_has_product_page_fields(self):
        data = self.client.get(reverse("candle-detail", args=["roadster"])).data
        self.assertEqual(data["scents"], ["Unscented", "Pine"])
        self.assertEqual(data["burn_time"], "~25 hours")
        self.assertEqual(data["size"], "14 × 7 × 8 cm")
        self.assertEqual(data["details"], "Soy wax, cotton wick.")
        self.assertEqual(data["story_title"], "Brushstrokes")
        self.assertEqual(data["flame"], {"x": 47.6, "y": 86.5})
        self.assertEqual([g["label"] for g in data["gallery"]], ["Grille detail", "Wheel detail"])
        self.assertTrue(
            data["gallery"][0]["image"].startswith("http://testserver/media/candles/gallery/")
        )

    def test_list_stays_lightweight(self):
        item = self.client.get(reverse("candle-list")).data["results"][0]
        for field in ["scents", "gallery", "flame", "details", "related"]:
            self.assertNotIn(field, item)

    def test_flame_is_null_without_a_wick_position(self):
        make_candle(title="Plain")
        data = self.client.get(reverse("candle-detail", args=["plain"])).data
        self.assertIsNone(data["flame"])
        self.assertEqual(data["gallery"], [])
        self.assertEqual(data["scents"], [])

    def test_flame_needs_both_values_in_range(self):
        for x, y in [(Decimal("50"), None), (None, Decimal("50")), (Decimal("120"), Decimal("50"))]:
            candle = Candle(title="x", description="x", image="x.png", price=Decimal("1"),
                            flame_x=x, flame_y=y)
            with self.subTest(x=x, y=y), self.assertRaises(ValidationError):
                candle.full_clean()

    def test_detail_query_count_is_constant(self):
        for i in range(6):
            make_candle(title=f"Other {i}")
        make_collection(title="Bundle")
        # candle, scents, gallery, showcase, related candles (4 found: no collections query)
        with self.assertNumQueries(5):
            self.client.get(reverse("candle-detail", args=["roadster"]))


class RelatedItemsTests(MediaTestMixin, APITestCase):
    def related(self, name, slug):
        data = self.client.get(reverse(f"{name}-detail", args=[slug])).data
        return [item["title"] for item in data["related"]]

    def test_candle_related_prefers_same_type_and_skips_sold_out(self):
        make_candle(title="Campfire", product_type="set")
        make_candle(title="Single A")
        make_candle(title="Sold out", stock=0)
        make_candle(title="Other set", product_type="set")
        make_candle(title="Featured single", is_featured=True)

        related = self.related("candle", "campfire")
        self.assertEqual(related[0], "Other set")  # same type first
        self.assertNotIn("Campfire", related)  # never itself
        self.assertNotIn("Sold out", related)
        self.assertEqual(related[1], "Featured single")  # then featured first

    def test_related_is_limited_and_filled_with_the_other_kind(self):
        make_candle(title="Main")
        make_candle(title="Second")
        make_collection(title="Bundle A")
        make_collection(title="Bundle B")
        make_collection(title="Bundle C")

        self.assertEqual(len(self.related("candle", "main")), 4)
        self.assertEqual(self.related("candle", "main")[0], "Second")

        collection_related = self.related("collection", "bundle-a")
        self.assertEqual(len(collection_related), 4)
        self.assertEqual(set(collection_related[:2]), {"Bundle B", "Bundle C"})


class ShowcaseApiTests(MediaTestMixin, APITestCase):
    def detail(self, slug):
        return self.client.get(reverse("candle-detail", args=[slug])).data

    def test_no_views_by_default(self):
        make_candle(title="Plain")
        self.assertEqual(self.detail("plain")["showcase_views"], [])

    def test_views_in_order_with_all_fields(self):
        candle = make_candle(title="Snowmen")
        CandleShowcaseView.objects.create(
            candle=candle, image=make_image("top.png"), label="From above", short_label="Top",
            caption="Snowy base.", color="#E9A23B", tint="#F6EFE2", group="top", order=2,
        )
        CandleShowcaseView.objects.create(
            candle=candle, image=make_image("front.png"), label="Front", order=1
        )
        front, top = self.detail("snowmen")["showcase_views"]
        self.assertEqual(front["label"], "Front")
        self.assertEqual(front["short_label"], "Front")  # falls back to the label
        self.assertEqual(front["group"], "side")
        self.assertEqual(
            {k: top[k] for k in ["short_label", "caption", "color", "tint", "group"]},
            {"short_label": "Top", "caption": "Snowy base.", "color": "#E9A23B",
             "tint": "#F6EFE2", "group": "top"},
        )
        self.assertTrue(top["image"].startswith("http://testserver/media/showcase/"))

    def test_colours_are_validated(self):
        view = CandleShowcaseView(
            candle=make_candle(), image="x.png", label="Front", color="green"
        )
        with self.assertRaises(ValidationError) as ctx:
            view.full_clean()
        self.assertIn("color", ctx.exception.message_dict)

    def test_list_has_no_showcase(self):
        make_candle()
        item = self.client.get(reverse("candle-list")).data["results"][0]
        self.assertNotIn("showcase_views", item)

    def test_admin_edits_views_on_the_product(self):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_superuser("admin", "a@a.com", "pw"))
        candle = make_candle()
        CandleShowcaseView.objects.create(candle=candle, image=make_image("f.png"), label="Front view")
        page = self.client.get(reverse("admin:shop_candle_change", args=[candle.pk]))
        self.assertContains(page, "Showcase views")
        self.assertContains(page, "Front view")
