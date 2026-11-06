import shutil
import tempfile
from pathlib import Path

from django.test import RequestFactory, SimpleTestCase, override_settings

from .views import serve_media


class SpaIndexTests(SimpleTestCase):
    """Django serves the built React app for page URLs, but not for the API or admin."""

    def setUp(self):
        self.dist = Path(tempfile.mkdtemp())
        (self.dist / "index.html").write_text("<!doctype html><div id=root></div>", encoding="utf-8")

    def test_page_urls_get_the_react_index(self):
        with override_settings(FRONTEND_DIST=self.dist):
            for url in ["/", "/candles/vintage-roadster-candle", "/decorate", "/no-such-page"]:
                with self.subTest(url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'id=root', b"".join(response.streaming_content))
                    self.assertIn("no-cache", response["Cache-Control"])

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
