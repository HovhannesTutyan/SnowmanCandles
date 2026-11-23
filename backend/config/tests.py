import shutil
import tempfile
from pathlib import Path

from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from .views import serve_media


class SpaIndexTests(TestCase):
    """Django serves the built React app for page URLs, but not for the API or admin."""

    def setUp(self):
        self.dist = Path(tempfile.mkdtemp())
        (self.dist / "index.html").write_text("<!doctype html><div id=root></div>", encoding="utf-8")

    def test_page_urls_get_the_react_index(self):
        with override_settings(FRONTEND_DIST=self.dist):
            for url in ["/", "/en/decorate", "/ru/candle-care"]:
                with self.subTest(url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b"id=root", response.content)
                    self.assertIn("no-cache", response["Cache-Control"])
            # Unknown pages still get the app (which shows "not found"), with a real 404.
            self.assertEqual(self.client.get("/no-such-page").status_code, 404)

    def test_api_and_admin_are_not_swallowed(self):
        with override_settings(FRONTEND_DIST=self.dist):
            self.assertEqual(self.client.get("/api/no-such-endpoint/").status_code, 404)
            self.assertEqual(self.client.get("/admin/").status_code, 302)  # to the login page

    def test_missing_build_is_a_404(self):
        with override_settings(FRONTEND_DIST=self.dist / "missing"):
            self.assertEqual(self.client.get("/decorate").status_code, 404)


class MediaRangeTests(SimpleTestCase):
    """Videos must be served in pieces for Safari/iPhones (HTTP 206)."""

    def setUp(self):
        self.media = tempfile.mkdtemp()
        Path(self.media, "clip.mp4").write_bytes(bytes(range(256)) * 4)  # 1024 bytes

    def tearDown(self):
        shutil.rmtree(self.media, ignore_errors=True)

    def get(self, **headers):
        request = RequestFactory().get("/media/clip.mp4", headers=headers)
        return serve_media(request, "clip.mp4", document_root=self.media)

    def test_whole_file_advertises_ranges(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Accept-Ranges"], "bytes")

    def test_range_request_returns_partial_content(self):
        response = self.get(Range="bytes=0-1")
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response["Content-Range"], "bytes 0-1/1024")
        self.assertEqual(b"".join(response.streaming_content), b"\x00\x01")

    def test_open_ended_and_suffix_ranges(self):
        self.assertEqual(self.get(Range="bytes=1000-")["Content-Range"], "bytes 1000-1023/1024")
        response = self.get(Range="bytes=-4")
        self.assertEqual(response["Content-Range"], "bytes 1020-1023/1024")
        self.assertEqual(len(b"".join(response.streaming_content)), 4)

    def test_range_past_the_end(self):
        self.assertEqual(self.get(Range="bytes=5000-6000").status_code, 416)


class MediaCacheTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "photo.webp").write_bytes(b"0123456789")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_uploaded_files_are_cached_by_browsers(self):
        request = RequestFactory().get("/media/photo.webp")
        response = serve_media(request, "photo.webp", document_root=self.root)
        self.assertEqual(response["Cache-Control"], "public, max-age=2592000")
        request = RequestFactory().get("/media/photo.webp", HTTP_RANGE="bytes=0-3")
        partial = serve_media(request, "photo.webp", document_root=self.root)
        self.assertEqual(partial.status_code, 206)
        self.assertEqual(partial["Cache-Control"], "public, max-age=2592000")


class PublicAddressTests(TestCase):
    """Production: https everywhere, one host."""

    @override_settings(
        SITE_URL="https://shop.example",
        MEDIA_URL="https://shop.example/media/",
        ALLOWED_HOSTS=["shop.example", "www.shop.example", "testserver"],
    )
    def test_image_addresses_use_the_public_https_address(self):
        from shop.testing import TEMP_MEDIA_ROOT, make_candle

        with override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT):
            make_candle(title="Https Candle")
            # The request itself arrives over plain http (from the web server in front).
            data = self.client.get("/api/candles/", HTTP_HOST="shop.example").json()
        self.assertTrue(data["results"][0]["image"].startswith("https://shop.example/media/"))

    def test_www_goes_to_the_main_address(self):
        # A new Client, so the middleware is set up again with these settings.
        with override_settings(
            SITE_URL="https://shop.example", ALLOWED_HOSTS=["shop.example", "www.shop.example"]
        ):
            response = self.client_class().get("/en/decorate?x=1", HTTP_HOST="www.shop.example")
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://shop.example/en/decorate?x=1")
            # The main address itself isn't redirected.
            response = self.client_class().get("/api/site/", HTTP_HOST="shop.example")
            self.assertEqual(response.status_code, 200)

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
        ALLOWED_HOSTS=["shop.example"],
    )
    def test_http_goes_to_https(self):
        response = self.client.get("/api/site/", HTTP_HOST="shop.example")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://shop.example/api/site/")
        # Requests the web server received over https are answered normally.
        response = self.client.get(
            "/api/site/", HTTP_HOST="shop.example", HTTP_X_FORWARDED_PROTO="https"
        )
        self.assertEqual(response.status_code, 200)
