from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from shop.models import Scent
from shop.testing import MediaTestMixin, make_candle, make_collection

from .models import Order


def customer(**overrides):
    return {
        "full_name": "Anna Petrosyan",
        "phone": "+374 91 234567",
        "email": "anna@example.com",
        "city": "Yerevan",
        "address": "Abovyan 10, apt 5",
        "notes": "Please call before delivery",
        "language": "hy",
        **overrides,
    }


class CartQuoteTests(MediaTestMixin, APITestCase):
    url = reverse("cart-quote")

    def setUp(self):
        self.candle = make_candle(title="Holly Bauble Candle", price="24.00", stock=3)
        self.candle.title_hy = "Գնդիկ-մոմ"
        self.candle.save()
        self.pine = Scent.objects.create(name="Pine & cedar", name_hy="Սոճի և մայրի", name_ru="Сосна и кедр")
        self.candle.scents.add(self.pine)

    def quote(self, items, lang="en"):
        return self.client.post(f"{self.url}?lang={lang}", {"items": items}, format="json")

    def test_returns_current_details_in_the_requested_language(self):
        response = self.quote(
            [{"kind": "candle", "slug": self.candle.slug, "scent": "Pine & cedar", "quantity": 2}], lang="hy"
        )
        self.assertEqual(response.status_code, 200)
        line = response.data["lines"][0]
        self.assertEqual(line["title"], "Գնդիկ-մոմ")
        self.assertEqual(line["scent"], "Սոճի և մայրի")  # stored in English, shown in Armenian
        self.assertEqual(line["price"], "24.00")
        self.assertEqual(line["line_total"], "48.00")
        self.assertEqual(line["stock"], 3)
        self.assertTrue(line["image"].startswith("http://testserver/media/"))
        self.assertEqual(response.data["total"], "48.00")

    def test_unknown_products_come_back_as_null_in_place(self):
        response = self.quote([
            {"kind": "candle", "slug": "gone", "quantity": 1},
            {"kind": "candle", "slug": self.candle.slug, "quantity": 1},
        ])
        self.assertIsNone(response.data["lines"][0])
        self.assertEqual(response.data["lines"][1]["slug"], self.candle.slug)
        self.assertEqual(response.data["total"], "24.00")

    def test_sold_out_lines_are_not_counted(self):
        sold_out = make_candle(title="Gone", price="10.00", stock=0)
        response = self.quote([{"kind": "candle", "slug": sold_out.slug, "quantity": 1}])
        self.assertEqual(response.data["lines"][0]["stock"], 0)
        self.assertEqual(response.data["total"], "0.00")

    def test_rejects_bad_lines(self):
        self.assertEqual(self.quote([{"kind": "jar", "slug": "x", "quantity": 1}]).status_code, 400)
        self.assertEqual(self.quote([{"kind": "candle", "slug": "x", "quantity": 0}]).status_code, 400)
        self.assertEqual(self.quote([{"kind": "candle", "slug": "x", "quantity": 99}]).status_code, 400)

    def test_works_for_signed_in_admins_without_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(get_user_model().objects.create_superuser("boss", password="pw-12345678"))
        response = client.post(self.url, {"items": []}, format="json")
        self.assertEqual(response.status_code, 200)


class OrderCreateTests(MediaTestMixin, APITestCase):
    url = reverse("order-create")

    def setUp(self):
        cache.clear()  # throttling counts
        self.candle = make_candle(title="Holly Bauble Candle", price="24.00", stock=3)
        self.collection = make_collection(title="Winter Set", price="60.00", stock=1)
        Scent.objects.create(name="Unscented", name_hy="Առանց բույրի")
        self.candle.scents.add(Scent.objects.get(name="Unscented"))

    def order(self, items, **fields):
        return self.client.post(self.url, {"items": items, **customer(**fields)}, format="json")

    def test_places_an_order_with_server_prices_and_takes_stock(self):
        response = self.order([
            {"kind": "candle", "slug": self.candle.slug, "scent": "Առանց բույրի", "quantity": 2, "price": "0.01"},
            {"kind": "collection", "slug": self.collection.slug, "quantity": 1},
        ])
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        self.assertEqual(response.data, {"number": order.number, "total": "108.00"})
        self.assertEqual(order.total, Decimal("108.00"))
        self.assertEqual(order.status, Order.Status.NEW)
        self.assertEqual(order.language, "hy")
        self.assertEqual(order.full_name, "Anna Petrosyan")
        first, second = order.items.all()
        self.assertEqual((first.title, first.scent, first.quantity), ("Holly Bauble Candle", "Unscented", 2))
        self.assertEqual(second.collection, self.collection)
        self.candle.refresh_from_db()
        self.collection.refresh_from_db()
        self.assertEqual((self.candle.stock, self.collection.stock), (1, 0))

    def test_too_few_in_stock_changes_nothing(self):
        response = self.order([
            {"kind": "candle", "slug": self.candle.slug, "quantity": 1},
            {"kind": "collection", "slug": self.collection.slug, "quantity": 2},
        ])
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["problems"], [{"index": 1, "available": 1}])
        self.assertFalse(Order.objects.exists())
        self.candle.refresh_from_db()
        self.assertEqual(self.candle.stock, 3)

    def test_same_product_in_two_scents_counts_together(self):
        response = self.order([
            {"kind": "candle", "slug": self.candle.slug, "scent": "Unscented", "quantity": 2},
            {"kind": "candle", "slug": self.candle.slug, "scent": "", "quantity": 2},
        ])
        self.assertEqual(response.status_code, 409)

    def test_required_fields_and_phone(self):
        response = self.order([{"kind": "candle", "slug": self.candle.slug, "quantity": 1}],
                              full_name="", phone="abc", city="", address="")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {"full_name", "phone", "city", "address"})
        self.assertEqual(self.order([], ).status_code, 400)  # empty basket

    def test_email_is_optional(self):
        response = self.order([{"kind": "candle", "slug": self.candle.slug, "quantity": 1}], email="")
        self.assertEqual(response.status_code, 201)

    def test_honeypot_blocks_bots(self):
        response = self.order([{"kind": "candle", "slug": self.candle.slug, "quantity": 1}], website="spam.biz")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())


class OrderAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("boss", password="pw-12345678"))
        self.candle = make_candle(title="Carousel Candle", price="42.00", stock=5)
        cache.clear()
        APIClient().post(reverse("order-create"), {
            "items": [{"kind": "candle", "slug": self.candle.slug, "quantity": 2}], **customer(),
        }, format="json")
        self.order = Order.objects.get()

    def test_list_detail_and_home_panel(self):
        response = self.client.get(reverse("admin:orders_order_changelist"))
        self.assertContains(response, self.order.number)
        self.assertContains(response, "Anna Petrosyan")
        response = self.client.get(reverse("admin:orders_order_change", args=[self.order.pk]))
        self.assertContains(response, "Carousel Candle")
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "1 new order")
        self.assertContains(response, "Translations")

    def test_cancel_action_restocks_once(self):
        url = reverse("admin:orders_order_changelist")
        for _ in range(2):
            self.client.post(url, {"action": "mark_cancelled", "_selected_action": [self.order.pk]})
        self.candle.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)
        self.assertEqual(self.candle.stock, 5)

    def test_cancelling_from_the_form_restocks_and_cannot_be_reopened(self):
        url = reverse("admin:orders_order_change", args=[self.order.pk])
        data = {
            "status": "cancelled", "admin_notes": "", "full_name": "Anna Petrosyan",
            "phone": "+374 91 234567", "email": "", "city": "Yerevan", "address": "Abovyan 10",
            "notes": "", "items-TOTAL_FORMS": "1", "items-INITIAL_FORMS": "1",
            "items-MIN_NUM_FORMS": "0", "items-MAX_NUM_FORMS": "1000",
            "items-0-id": str(self.order.items.get().pk), "items-0-order": str(self.order.pk),
        }
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.candle.refresh_from_db()
        self.assertEqual(self.candle.stock, 5)
        response = self.client.post(url, {**data, "status": "confirmed"})
        self.assertContains(response, "can&#x27;t be reopened")

    def test_orders_cannot_be_added_by_hand(self):
        self.assertEqual(self.client.get(reverse("admin:orders_order_add")).status_code, 403)
