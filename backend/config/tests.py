import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings


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
