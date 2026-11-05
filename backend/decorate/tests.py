import io

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from shop.testing import MediaTestMixin, make_candle, make_image

from .models import DecoratePage, GalleryImage, Room


def make_picture(caption, order=0, **kwargs):
    return GalleryImage.objects.create(
        image=make_image(f"{caption}.png"), caption=caption, alt=f"{caption} alt", order=order, **kwargs
    )


class DecorateApiTests(MediaTestMixin, APITestCase):
    url = reverse("decorate")

    def test_default_texts_and_rooms(self):
        data = self.client.get(self.url).data
        self.assertEqual(data["hero_title"], "Decorate\nwith light")
        self.assertIn("**living room**", data["story_text"])
        self.assertEqual(
            [r["title"] for r in data["rooms"]],
            ["Living room", "Bedroom", "Bathroom", "Dining table", "Entryway", "Terrace & garden"],
        )
        self.assertIsNone(data["rooms"][0]["gallery_index"])  # no pictures yet
        self.assertEqual(data["gallery"], [])
        self.assertIsNone(data["hero_image"])
        self.assertIsNone(data["cta_image"])
        self.assertNotIn("id", data)

    def test_default_texts_mention_no_jars_or_keepsakes(self):
        page = DecoratePage.load()
        texts = " ".join([page.hero_text, page.hero_image_alt, page.story_text, page.cta_text]
                         + [f"{r.title} {r.text}" for r in page.rooms.all()]).lower()
        for word in ["jar", "keepsake", "figurine", "["]:
            self.assertNotIn(word, texts)

    def test_gallery_order_visibility_and_products(self):
        roadster = make_candle(title="Roadster")
        second = make_picture("Second", order=2)
        first = make_picture("First", order=1)
        make_picture("Hidden", order=0, is_published=False)
        first.products.set([roadster])

        gallery = self.client.get(self.url).data["gallery"]
        self.assertEqual([g["caption"] for g in gallery], ["First", "Second"])
        self.assertEqual(gallery[0]["products"], [{"title": "Roadster", "slug": "roadster", "product_type": "candle"}])
        self.assertTrue(gallery[0]["image"].startswith("http://testserver/media/decorate/gallery/"))
        self.assertEqual(gallery[1]["alt"], "Second alt")
        self.assertEqual(second.products.count(), 0)

    def test_rooms_point_at_their_picture_position(self):
        page = DecoratePage.load()
        a = make_picture("A", order=1)
        hidden = make_picture("Hidden", order=2, is_published=False)
        b = make_picture("B", order=3)
        rooms = list(page.rooms.all())
        rooms[0].picture = b
        rooms[1].picture = hidden
        rooms[2].picture = a
        for room in rooms[:3]:
            room.save()

        data = self.client.get(self.url).data
        indexes = [r["gallery_index"] for r in data["rooms"][:3]]
        self.assertEqual(indexes, [1, None, 0])  # B is 2nd once Hidden is left out

    def test_deleting_a_picture_keeps_the_room(self):
        picture = make_picture("Gone")
        room = Room.objects.first()
        room.picture = picture
        room.save()
        picture.delete()
        room.refresh_from_db()
        self.assertIsNone(room.picture)

    def test_query_count_is_constant(self):
        candle = make_candle()
        for i in range(6):
            make_picture(f"P{i}", order=i).products.set([candle])
        # page, gallery, products, rooms
        with self.assertNumQueries(4):
            self.client.get(self.url)


class DecorateAdminTests(MediaTestMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("admin", "a@a.com", "pw")
        self.client.force_login(user)

    def test_page_form_with_room_inlines(self):
        response = self.client.get(reverse("admin:decorate_decoratepage_changelist"))
        change_url = reverse("admin:decorate_decoratepage_change", args=[1])
        self.assertRedirects(response, change_url)
        page = self.client.get(change_url)
        self.assertContains(page, "Living room")
        self.assertContains(page, "Using the picture from the original design.")

    def test_gallery_admin(self):
        make_picture("Shelf")
        self.assertContains(self.client.get(reverse("admin:decorate_galleryimage_changelist")), "Shelf")
        self.assertEqual(self.client.get(reverse("admin:decorate_galleryimage_add")).status_code, 200)


class SeedDemoDecorateTests(MediaTestMixin, TestCase):
    def test_seed_uploads_gallery_and_links_rooms_once(self):
        call_command("seed_demo", stdout=io.StringIO())
        call_command("seed_demo", stdout=io.StringIO())
        self.assertEqual(GalleryImage.objects.count(), 16)
        living = Room.objects.get(title="Living room")
        self.assertEqual(living.picture.caption, "Carousel Candle + Holly Bauble on a linen shelf")
        self.assertEqual(
            set(living.picture.products.values_list("title", flat=True)),
            {"Carousel Candle", "Holly Bauble Candle"},
        )
